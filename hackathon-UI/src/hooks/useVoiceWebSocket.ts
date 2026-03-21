import { useEffect, useState } from "react";

export default function useVoiceWebSocket() {
  const [commands, setCommands] = useState<string[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onmessage = (event) => {
      setCommands((prev) => [...prev, event.data]);
    };

    ws.onclose = () => console.log("WebSocket disconnected");
    ws.onerror = (err) => console.error("WebSocket error:", err);

    return () => ws.close();
  }, []);

  return commands;
}