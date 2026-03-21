import "../styles/DroneStatus.css";
import useVoiceWebSocket from "../hooks/useVoiceWebSocket";

export default function DroneStatus() {
  const wsCommands = useVoiceWebSocket();

  const droneColors: Record<string, string> = {
    "Drone Alpha": "orangered",
    "Drone Bravo": "yellowgreen",
  };

  // Simple parsing: color by drone keyword
  const parsedCommands = wsCommands.map((cmd) => {
    if (cmd.toLowerCase().includes("alpha")) {
      return { drone: "Drone Alpha", action: cmd };
    } else if (cmd.toLowerCase().includes("bravo")) {
      return { drone: "Drone Bravo", action: cmd };
    } else {
      return { drone: "Unknown", action: cmd };
    }
  });

  return (
    <div className="status">
      <div className="terminalContent">
        {parsedCommands.map((cmd, i) => (
          <p key={i}>
            <span style={{ color: droneColors[cmd.drone] || "#00eaff" }}>
              {cmd.drone}
            </span>: {cmd.action}
          </p>
        ))}
        <span className="terminalCursor">_</span>
      </div>
    </div>
  );
}