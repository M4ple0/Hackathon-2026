#listens to the mic to collect audio frames until it detects silence
import pyaudio
import webrtcvad
import numpy as np
import collections
import subprocess
from faster_whipser import WhisperModel
sample_rate = 16000
frame_ms = 30
frame_bytes = int(sample_rate * frame_ms / 1000) * 2
silence_timeout = 20

def capture_utterance() -> bytes:
    """Records from mic until the operator stops speaking"""
    vad = webrtcvad.Vad(2)
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16, 
        channels=1,
        rate=sample_rate,
        frames_per_buffer=frame_bytes // 2
    )

    frames = []
    silent_frames = 0
    speaking = False
    print("Listening...")
    while True:
        frame = stream.read(frame_bytes // 2, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech:
            speaking: True
            silent_frames = 0
            frames.append(frame)
        elif speaking:
            silent_frames +=  1
            frames.append(frame)
            if silent_frames > silence_timeout:
                break
        stream.stop_stream()
        stream.close()
        return b"".join(frames)
#converts audio bytes into numpy array for whisper and returns the text and a confidence score
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe(audio_bytes: bytes) -> tuple[str, float]:
    #Returns (text, confidence) from raw audio bytes

    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio_np /= 32768.0

    segments, info = model.transcribe(audio_np, language="en")

    text = " ".join(seg.text.strip() for seg in segments)

    all_segs = list(model.transcribe(audio_np, language="en")[0])
    if not all_segs:
        return "", 0.0
    
    avg_prob = sum(s.avg_logprob for s in all_segs) / len(all_segs)

    confidence = max(0.0, min(1.0, 1.0 + avg_prob))

    return text.strip(), confidence

wake_words = ["drone", "activate", "control", "command", "computer"]

def has_wake_word(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in wake_words)

confidence_threshold = 0.5

def stt_loop(on_command):
    #Runs forever. Calls on_command(text) whenever a valid command is captured with confidence

    print("System Ready. Say a wake word to begin")

    while True:
        audio = capture_utterance()
        text, confidence = transcribe(audio)
        print(f"Heard: '{text}' (confidence: {confidence:.2f})")
        if not text:
            continue

        if not has_wake_word(text):
            print("No wake word detected, ignoring command")
            continue
        if confidence < confidence_threshold:
            print(f"Low confidence ({confidence:.2f}). Please repeat")
            speak("Sorry, I couldn't understand that, please repeat your command")
            continue

        print(f"command accepted: '{text}'")
        on_command(text)

def speak(message: str);
    #TTS using system voice can swap for a better library later
    import subprocess
    subprocess.run(["say", message])

def handle_command(text: str):
    print(f"Sending to parser: {text}")

if __name__ == "__main__";
    stt_loop(on_command=handle_command)

    #code test
def run_test():
    test_commands = [
        "drone fly to bravo",
        "drone return to base",
        "activate engage hostile target"
        "activate orbit charlie",
        "control land",
        "control check battery level",
        "computer abort mission",
        "computer go north",
        "command return to alpha",
        "command destroy bravo",
    ]
    results = []
    for i, expected in enumerate(test_commands):
        input(f"\nTest {i + 1}/{len(test_commands)}: Say '{expected}' the press enter to start recording...")
        audio = capture_utterance()
        text, confidence = transcribe(audio)
        passed = confidence >= confidence_threshold
        results.append({
            "expected": expected,
            "heard": text,
            "confidence": round(confidence, 2),
            "passed": passed
        })
        print(f"Heard: '{text}'")
        print(f"Confidence: {confidence:.2f} ({'PASS' if passed else 'FAIL'})")

        print("\n Test Results")
        passed = sum(1 or r in results if r["passed"])
        print(f"{passed}/{len(results)} commands passed confidence gate")
        for r in results:
            status = "🤑" if r["passed"] else "🤬"
            print(f" {status} {r['expected']}")
            if not r["passed"]:
                print(f" heard: '{r['heard']}' ({r['confidence']})")