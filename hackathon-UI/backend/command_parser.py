
"""
command_parser.py — LLM-powered voice command parser for drone C2 system

Converts raw STT transcript text into structured ParsedCommand JSON,
ready to pass directly into SafetyEngine.validate().

Usage:
    parser = CommandParser()
    cmd = parser.parse("Take drone Alpha up to 30 metres and fly to waypoint Bravo")
    result = safety_engine.validate(cmd)
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass

import anthropic

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Battlespace context — update these on event day with the real data files
# ---------------------------------------------------------------------------

WAYPOINTS = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]

ENTITIES = [
    {"id": "f-01", "name": "Falcon-1",  "classification": "FRIENDLY"},
    {"id": "f-02", "name": "Eagle-2",   "classification": "FRIENDLY"},
    {"id": "u-01", "name": "Contact-3", "classification": "UNKNOWN"},
    {"id": "h-01", "name": "Tango-1",   "classification": "HOSTILE"},
    {"id": "h-02", "name": "Tango-2",   "classification": "HOSTILE"},
]

DRONES = ["Alpha", "Bravo"]

# ---------------------------------------------------------------------------
# The system prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a voice command parser for a military drone command-and-control system.
Your only job is to convert a spoken operator command into a structured JSON object.

Output ONLY valid JSON. No explanation, no markdown, no code fences. Just the JSON object.

## Output schema

{{
  "action":      string,        // one of the actions listed below
  "drone":       string|null,   // "Alpha", "Bravo", "all", or null if not specified
  "target":      string|null,   // waypoint name, entity name/ID, or null
  "altitude_m":  number|null,   // numeric metres — convert feet/km if needed, else null
  "confidence":  number,        // 0.0–1.0: how clearly the command was understood
  "ambiguous":   boolean,       // true if the command could mean more than one thing
  "compound":    boolean,       // true if the input contains multiple distinct commands
  "sub_commands": array|null,   // if compound=true, array of command objects (same schema, no sub_commands)
  "raw_input":   string         // the original text, unchanged
}}

## Valid actions

| action        | meaning                                      |
|---------------|----------------------------------------------|
| takeoff       | launch and climb to altitude                 |
| land          | descend and land at current position         |
| fly_to        | navigate to a waypoint or GPS position       |
| rtl           | return to launch point and land              |
| hover         | hold current position                        |
| engage        | attack / fire on a target                   |
| investigate   | approach and observe a target                |
| track         | maintain sensor lock on a moving target      |
| unknown       | command could not be understood              |

## Battlespace reference

Drones available : {", ".join(DRONES)}
Waypoints        : {", ".join(WAYPOINTS)}

Known contacts:
{json.dumps(ENTITIES, indent=2)}

## Parsing rules

### Drone selection
- "both drones" / "all drones" → drone: "all"
- If only one drone exists in context and none is named → drone: null, ambiguous: true
- Drone names are case-insensitive ("drone alpha" → "Alpha")

### Targets
- Waypoints: normalise to Title Case ("waypoint bravo" → "Bravo")
- Entities: match by name or ID, case-insensitive ("tango one" → "Tango-1", "t-1" → "Tango-1")
- Never invent a target that isn't in the lists above

### Altitude
- Convert feet → metres (1 ft = 0.3048 m), round to 1 decimal place
- Convert km → metres
- "low altitude", "high altitude" → null (ambiguous, not a specific number)
- Negative or zero altitudes → still capture the value (safety engine will reject it)

### Compound commands
- "take off and fly to Alpha" → compound: true, sub_commands: [takeoff obj, fly_to obj]
- Each sub-command is a full command object (minus the sub_commands field)
- If sub-commands conflict ("take off and land") → compound: true, ambiguous: true

### Confidence scoring
- Clear, unambiguous command with known targets → 0.90–1.00
- Minor uncertainty (one unclear word, inferred drone) → 0.70–0.89
- Significant uncertainty (unknown target name, very unclear speech) → 0.50–0.69
- Command barely parseable → 0.30–0.49
- Cannot parse at all → action: "unknown", confidence: 0.10–0.30

### When to set ambiguous: true
- Multiple valid interpretations exist
- Drone not specified and more than one is available
- Target name could match more than one entity or waypoint
- Instruction is grammatically incomplete

### Phonetic alphabet & common mishearings
Map these to standard names:
alpha→Alpha, bravo→Bravo, charlie→Charlie, delta→Delta, echo→Echo,
foxtrot→Foxtrot, golf→Golf, hotel→Hotel
"tango one"→Tango-1, "tango two"→Tango-2
"eagle two"→Eagle-2, "falcon one"→Falcon-1, "contact three"→Contact-3
"RTL" / "return to base" / "come home" / "go home" → action: "rtl"
"hold" / "hold position" / "stay" / "freeze" → action: "hover"

## Examples

Input : "Take drone Alpha up to 20 metres"
Output: {{"action":"takeoff","drone":"Alpha","target":null,"altitude_m":20,"confidence":0.97,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"Take drone Alpha up to 20 metres"}}

Input : "Fly to Waypoint Bravo"
Output: {{"action":"fly_to","drone":null,"target":"Bravo","altitude_m":null,"confidence":0.85,"ambiguous":true,"compound":false,"sub_commands":null,"raw_input":"Fly to Waypoint Bravo"}}

Input : "Send both drones to Waypoint Charlie at 50 feet"
Output: {{"action":"fly_to","drone":"all","target":"Charlie","altitude_m":15.2,"confidence":0.95,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"Send both drones to Waypoint Charlie at 50 feet"}}

Input : "Take off and investigate the unknown contact"
Output: {{"action":null,"drone":null,"target":null,"altitude_m":null,"confidence":0.88,"ambiguous":false,"compound":true,"sub_commands":[{{"action":"takeoff","drone":null,"target":null,"altitude_m":null,"confidence":0.95,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"Take off and investigate the unknown contact"}},{{"action":"investigate","drone":null,"target":"Contact-3","altitude_m":null,"confidence":0.90,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"Take off and investigate the unknown contact"}}],"raw_input":"Take off and investigate the unknown contact"}}

Input : "uh... send the thing to... bravo maybe?"
Output: {{"action":"fly_to","drone":null,"target":"Bravo","altitude_m":null,"confidence":0.52,"ambiguous":true,"compound":false,"sub_commands":null,"raw_input":"uh... send the thing to... bravo maybe?"}}

Input : "engage Falcon-1"
Output: {{"action":"engage","drone":null,"target":"Falcon-1","altitude_m":null,"confidence":0.97,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"engage Falcon-1"}}

Input : "xzqt drone flibber"
Output: {{"action":"unknown","drone":null,"target":null,"altitude_m":null,"confidence":0.15,"ambiguous":false,"compound":false,"sub_commands":null,"raw_input":"xzqt drone flibber"}}
"""

# ---------------------------------------------------------------------------
# Parser class
# ---------------------------------------------------------------------------

@dataclass
class CommandParser:
    """
    Wraps the Anthropic API to parse STT transcript text into command dicts.
    The returned dict is ready to pass directly to SafetyEngine.validate().
    """
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 512

    def __post_init__(self):
        self._client = anthropic.Anthropic(
            api_key= "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"  #"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"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, transcript: str) -> dict:
        """
        Parse a raw STT transcript into a structured command dict.
        Always returns a valid dict — never raises on API or JSON errors.
        """
        transcript = transcript.strip()
        if not transcript:
            return self._fallback(transcript, reason="empty input")

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": transcript}],
            )
            raw = response.content[0].text.strip()
            return self._parse_response(raw, transcript)

        except anthropic.APIError as e:
            logger.error("Anthropic API error: %s", e)
            return self._fallback(transcript, reason=f"API error: {e}")
        except Exception as e:
            logger.error("Unexpected parser error: %s", e)
            return self._fallback(transcript, reason=str(e))

    def parse_compound(self, transcript: str) -> list[dict]:
        """
        Convenience wrapper: if the parsed command is compound, returns the
        list of sub-commands. Otherwise returns a single-item list.
        Useful for iterating commands straight into the safety engine.
        """
        result = self.parse(transcript)
        if result.get("compound") and result.get("sub_commands"):
            return result["sub_commands"]
        return [result]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str, original: str) -> dict:
        """Strip any accidental markdown fences and parse JSON."""
        # Strip ```json ... ``` or ``` ... ``` if the model adds them anyway
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()

        try:
            cmd = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning("JSON parse failed: %s\nRaw output: %s", e, raw)
            return self._fallback(original, reason="JSON decode error")

        # Guarantee raw_input is always the original transcript
        cmd["raw_input"] = original

        # Ensure all expected keys are present (defensive defaults)
        defaults = {
            "action":       "unknown",
            "drone":        None,
            "target":       None,
            "altitude_m":   None,
            "confidence":   0.5,
            "ambiguous":    False,
            "compound":     False,
            "sub_commands": None,
        }
        for key, value in defaults.items():
            cmd.setdefault(key, value)

        logger.debug("Parsed: %s", json.dumps(cmd))
        return cmd

    @staticmethod
    def _fallback(transcript: str, reason: str = "") -> dict:
        """Return a safe 'unknown' command when parsing fails entirely."""
        logger.warning("Parser fallback (%s) for: %r", reason, transcript)
        return {
            "action":       "unknown",
            "drone":        None,
            "target":       None,
            "altitude_m":   None,
            "confidence":   0.0,
            "ambiguous":    False,
            "compound":     False,
            "sub_commands": None,
            "raw_input":    transcript,
        }


# ---------------------------------------------------------------------------
# Quick self-test — run with: python command_parser.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    parser = CommandParser()

    test_inputs = [
        "Take drone Alpha up to 20 metres",
        "Fly to Waypoint Bravo",
        "Send both drones to Charlie at 50 feet",
        "Take off and investigate the unknown contact",
        "Engage Tango-1 with drone Bravo",
        "Engage Falcon-1",                          # should still parse — safety engine blocks it
        "Come home",                                # RTL alias
        "Hold position",                            # hover alias
        "uh... send the thing to... bravo maybe?",  # low confidence
        "",                                         # empty — fallback
    ]

    print("\n" + "=" * 64)
    print("  COMMAND PARSER — SELF TEST")
    print("=" * 64)

    for text in test_inputs:
        label = f'"{text}"' if text else "(empty string)"
        print(f"\nInput   : {label}")
        result = parser.parse(text)
        action     = result.get("action")
        drone      = result.get("drone", "—")
        target     = result.get("target", "—")
        alt        = result.get("altitude_m")
        confidence = result.get("confidence", 0)
        ambiguous  = result.get("ambiguous", False)
        compound   = result.get("compound", False)

        print(f"Action  : {action}")
        print(f"Drone   : {drone}  |  Target: {target}  |  Alt: {alt}m")
        print(f"Conf    : {confidence:.0%}  |  Ambiguous: {ambiguous}  |  Compound: {compound}")

        if compound and result.get("sub_commands"):
            for i, sub in enumerate(result["sub_commands"], 1):
                print(f"  Sub-{i} : {sub.get('action')} → drone={sub.get('drone')} "
                      f"target={sub.get('target')} alt={sub.get('altitude_m')}m")
