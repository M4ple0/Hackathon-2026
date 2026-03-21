from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from voice_listener import transcribe, confidence_threshold, has_wake_word
import webrtcvad
import pyaudio
import asyncio

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)

is_listening = False

def set_listening(state: bool):
    global is_listening
    is_listening = state

@app.get("/voice-status")
async def voice_status():
    return JSONResponse({"listening": is_listening})

def capture_utterance_with_flag(sample_rate=16000, frame_ms=30, silence_timeout=20):
    """
    Capture audio from mic.
    Returns (audio_bytes, heard_speech)
    Updates is_listening while user is actually speaking.
    """
    global is_listening
    vad = webrtcvad.Vad(2)
    audio = pyaudio.PyAudio()
    frame_bytes = int(sample_rate * frame_ms / 1000) * 2
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

    while True:
        frame = stream.read(frame_bytes // 2, exception_on_overflow=False)
        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech:
            if not speaking:
                is_listening = True
            speaking = True
            silent_frames = 0
            frames.append(frame)
        elif speaking:
            silent_frames += 1
            frames.append(frame)
            if silent_frames > silence_timeout:
                is_listening = False
                break
        else:
            frames.append(frame)

    stream.stop_stream()
    stream.close()
    audio.terminate()
    audio_bytes = b"".join(frames)
    return audio_bytes, speaking

async def async_capture_utterance():
    return await asyncio.to_thread(capture_utterance_with_flag)

async def listen_for_command(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Capture audio in thread
            audio_bytes, heard_speech = await async_capture_utterance()

            # Animate only if real speech detected
            if heard_speech:
                set_listening(True)
            else:
                set_listening(False)

            text, confidence = transcribe(audio_bytes)

            if confidence >= confidence_threshold and has_wake_word(text):
                await websocket.send_text(text)

            # Stop animation after sending / processing
            set_listening(False)

            # Short cooldown before next capture
            await asyncio.sleep(0.5)

    except Exception as e:
        print("WebSocket closed:", e)

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await listen_for_command(websocket)

@app.get("/")
async def root():
    return {"status": "Voice server running"}