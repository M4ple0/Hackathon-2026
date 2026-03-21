from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from voice_listener import transcribe, confidence_threshold, has_wake_word
from command_parser import CommandParser
import webrtcvad
import pyaudio
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = CommandParser()
is_listening = False

def set_listening(state: bool):
    global is_listening
    is_listening = state

@app.get("/voice-status")
async def voice_status():
    return JSONResponse({"listening": is_listening})

def capture_utterance(sample_rate=16000, frame_ms=30, silence_timeout=20):
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

    return b"".join(frames), speaking

async def async_capture_utterance():
    return await asyncio.to_thread(capture_utterance)

async def listen_for_command(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            audio_bytes, heard_speech = await async_capture_utterance()

            if not heard_speech:
                continue

            text, confidence = transcribe(audio_bytes)

            if confidence < confidence_threshold or not has_wake_word(text):
                continue

            commands = parser.parse_compound(text)

            response_payload = []

            for cmd in commands:
                if cmd.get("confidence", 0) < 0.4:
                    response_payload.append({
                        "type": "error",
                        "message": "Command unclear"
                    })
                    continue

                response_payload.append({
                    "type": "command",
                    "action": cmd.get("action"),
                    "drone": cmd.get("drone"),
                    "target": cmd.get("target"),
                    "altitude": cmd.get("altitude_m"),
                    "confidence": cmd.get("confidence")
                })

            await websocket.send_text(json.dumps({
                "transcript": text,
                "commands": response_payload
            }))

            await asyncio.sleep(0.3)

    except Exception as e:
        print("WebSocket closed:", e)
        set_listening(False)

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await listen_for_command(websocket)

@app.get("/")
async def root():
    return {"status": "Voice server running"}