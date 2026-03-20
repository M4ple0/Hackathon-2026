#listens to the mic to collect audio frames until it detects silence
import pyaudio
import webrtcvad
import numpy as np
import collections
import subprocess
from faster_whisper import WhisperModel
import pyttsx3

sample_rate = 16000
frame_ms = 30
frame_bytes = int(sample_rate * frame_ms / 1000) * 2
silence_timeout = 20
system_active = True

def capture_utterance() -> bytes:
    vad = webrtcvad.Vad(2)
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_bytes // 2,
    )

    frames = []
    silent_frames = 0
    speaking = False

    print("Listening...")
    while True:
        frame = stream.read(frame_bytes // 2, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech:
            speaking = True        
            silent_frames = 0
            frames.append(frame)
        elif speaking:             
            silent_frames += 1
            frames.append(frame)
            if silent_frames > silence_timeout:
                break         
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return b"".join(frames)
#converts audio bytes into numpy array for whisper and returns the text and a confidence score
model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

def transcribe(audio_bytes: bytes) -> tuple[str, float]:
    #returns text and confidence from bytes
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio_np /= 32768.0

    segments, info = model.transcribe(audio_np, language="en")
    
    # Convert to list once — can only iterate segments once
    all_segs = list(segments)
    
    if not all_segs:
        return "", 0.0

    text = " ".join(seg.text.strip() for seg in all_segs)
    
    avg_logprob = sum(s.avg_logprob for s in all_segs) / len(all_segs)
    confidence = max(0.0, min(1.0, 1.0 + avg_logprob))

    return text.strip(), confidence
wake_words = ["drone", "activate", "control", "command", "computer"]
deactivate_words = "deactivate"
def has_wake_word(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in wake_words)

confidence_threshold = 0.15

def stt_loop(on_command):
    global system_active
    print("System ready. Say a wake word to begin. Say 'deactivate' to stop.")

    while system_active:
        audio = capture_utterance()
        text, confidence = transcribe(audio)
        print(f"Heard: '{text}' (confidence: {confidence:.3f})")

        if not text:
            continue

        # check for deactivate first before anything else
        if deactivate_words in text.lower():
            print("Deactivate word detected. Shutting down.")
            speak("System deactivated.")
            system_active = False
            break

        if not has_wake_word(text):
            print("No wake word detected, ignoring.")
            continue

        if confidence < confidence_threshold:
            print(f"Low confidence ({confidence:.3f}). Please repeat.")
            speak("Sorry, I could not understand that. Please repeat your command.")
            continue

        print(f"Command accepted: '{text}'")
        on_command(text)

#TTS using system voice can swap for a better library later
def speak(message: str):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()

def handle_command(text: str):
    print(f"Sending to parser: {text}")
    #code test

def run_test():
    test_commands = [
        "computer fly to bravo",
        "computer return to base",
        "computer engage hostile target",
        "computer orbit charlie",
        "computer land",
        "computer check battery level",
        "computer abort mission",
        "computer go north",
        "computer return to alpha",
        "computer destroy bravo",
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
    passed_count = sum(1 for r in results if r["passed"])
    print(f"{passed_count}/{len(results)} commands passed confidence gate")
    for r in results:
        status = "🤑" if r["passed"] else "🤬"
        print(f" {status} {r['expected']}")
        if not r["passed"]:
            print(f" heard: '{r['heard']}' ({r['confidence']})")

if __name__ == "__main__":
    run_test()
