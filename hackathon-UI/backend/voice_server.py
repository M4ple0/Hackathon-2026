# voice_server.py
from fastapi import FastAPI, WebSocket
import asyncio
from voice_listener import stt_loop
import threading

app = FastAPI()
clients: set[WebSocket] = set()

@app.websocket("/ws/voice")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await asyncio.sleep(1)
    except:
        pass
    finally:
        clients.remove(ws)

def send_to_clients(text: str):
    loop = asyncio.get_event_loop()
    for ws in list(clients):
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(text), loop)
        except:
            clients.remove(ws)

def handle_command(text: str):
    print(f"Command accepted: {text}")
    send_to_clients(text)

if __name__ == "__main__":
    # run STT in a separate thread so FastAPI remains responsive
    threading.Thread(target=lambda: stt_loop(handle_command), daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)