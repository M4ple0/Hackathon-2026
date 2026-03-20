import { useState } from "react";
import "../styles/DroneStatus.css";

type Command = {
  drone: "Drone Alpha" | "Drone Bravo";
  action: string;
};

export default function DroneStatus() {
  const [commands, setCommands] = useState<Command[]>([
    { drone: "Drone Alpha", action: "Initializing systems..." },
    { drone: "Drone Bravo", action: "Drone connection established." },
  ]);

  const droneColors: Record<string, string> = {
    "Drone Alpha": "orangered",
    "Drone Bravo": "yellowgreen",
  };

  return (
    <div className="status">
      <div className="terminalContent">
        {commands.map((cmd, i) => (
          <p key={i}>
            <span style={{ color: droneColors[cmd.drone] }}>{cmd.drone}</span>: {cmd.action}
          </p>
        ))}
      </div>
    </div>
  );
}