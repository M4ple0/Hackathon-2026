from __future__ import annotations
import json
import logging
import os
import re
import key
from dataclasses import dataclass
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)

prompt_file = open("parser_prompt.txt", "r+")

SYSTEM_PROMPT =  prompt_file.read()

@dataclass
class CommandParser:

    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 512

    def __post_init__(self):

        self.client = anthropic.Anthropic(
            api_key=key.API_KEY
        )

    def parse(self, transcript: str) -> dict:
        """
        Parse a raw STT transcript into a structured command dict.
        Always returns a valid dict — never raises on API or JSON errors.
        """
        transcript = transcript.strip()
        if not transcript:
            return self._fallback(transcript, reason="empty input")
        
        #fast = fast_parse(transcript) 
        #if fast: return fast
 
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
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
            "action":        "unknown",
            "drone":         None,
            "target":        None,
            "altitude_m":    None,
            "direction":     None,
            "distance_m":    None,
            "confidence":    0.5,
            "ambiguous":     False,
            "contradictory": False,
            "compound":      False,
            "sub_commands":  None,
            "rejected":      False,
            "reject_reason": None,
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
            "action":        "unknown",
            "drone":         None,
            "target":        None,
            "altitude_m":    None,
            "direction":     None,
            "distance_m":    None,
            "confidence":    0.5,
            "ambiguous":     False,
            "contradictory": False,
            "compound":      False,
            "sub_commands":  None,
            "rejected":      False,
            "reject_reason": None,
        }

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    parser = CommandParser()

    tests = [
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

    for t in tests:

        print("\nInput:", t)

        result = parser.parse(t)

        print(json.dumps(result, indent=2))

