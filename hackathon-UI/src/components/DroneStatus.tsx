import "../styles/DroneStatus.css";
import useVoiceWebSocket from "../hooks/useVoiceWebSocket";
import { useEffect, useRef } from "react";

type Props = {
  onWarning: () => void;
  onBlocked: (msg: string) => void;
};

export default function DroneStatus({ onWarning, onBlocked }: Props) {
  const wsCommands = useVoiceWebSocket();
  const lastCommand = useRef<string>("");

  const droneColors: Record<string, string> = {
    "Drone Alpha": "orangered",
    "Drone Bravo": "yellowgreen",
  };

  function checkCommand(cmd: string) {
    const text = cmd.toLowerCase();

    if (text.includes("nuke") || text.includes("self-destruct")) {
      onBlocked("Command is not allowed!");
      return;
    }

    if (text.includes("bomb") || text.includes("attack")) {
      onWarning();
    }
  }

  useEffect(() => {
    const latest = wsCommands[wsCommands.length - 1];

    if (!latest || latest === lastCommand.current) return;

    lastCommand.current = latest;
    checkCommand(latest);

  }, [wsCommands]);

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