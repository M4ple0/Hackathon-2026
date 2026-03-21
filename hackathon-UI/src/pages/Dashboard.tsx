import { useState } from "react";
import Radar from "../components/Radar";
import VoiceControl from "../components/VoiceControl";
import DroneStatus from "../components/DroneStatus";
import TelemertyPanel from "../components/TelemertyPanel";
import "../styles/Dashboard.css";

export default function Dashboard() {
  const [warning, setWarning] = useState(false);
  const [blocked, setBlocked] = useState<string | null>(null);

  // Determine danger color based on type
  let dangerColor = "";
  if (blocked) dangerColor = "red";
  else if (warning) dangerColor = "yellow";

  return (
    <div
      className={`dashboard ${dangerColor ? "danger-mode" : ""}`}
      data-danger={dangerColor}
    >
      {blocked && (
        <div className="warningOverlay">
          <div className="blockedPopup">
            <h2>BLOCKED COMMAND</h2>
            <p>{blocked}</p>
          </div>
        </div>
      )}

      {warning && (
        <div className="warningOverlay">
          <div className="warningPopup">
            <h2>⚠ HIGH RISK ACTION</h2>
            <p>Confirm command execution</p>
          </div>
        </div>
      )}

      <Radar />
      <VoiceControl />
      <DroneStatus 
      onWarning={() => setWarning(true)}
      onBlocked={(msg) => setBlocked(msg)}
      />
      <TelemertyPanel />
    </div>
  );
}