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
      {/* 🔴 BLOCKED POPUP */}
      {blocked && (
        <div className="warningOverlay">
          <div className="blockedPopup">
            <h2>BLOCKED COMMAND</h2>
            <p>{blocked}</p>
            <button className="blocked-button" onClick={() => setBlocked(null)}>Close</button>
          </div>
        </div>
      )}

      {/* 🟡 WARNING POPUP */}
      {warning && (
        <div className="warningOverlay">
          <div className="warningPopup">
            <h2>⚠ HIGH RISK ACTION</h2>
            <p>Confirm command execution</p>
            <button className="warning-button" onClick={() => setWarning(false)}>Confirm</button>
            <button className="warning-button" onClick={() => setWarning(false)}>Cancel</button>
          </div>
        </div>
      )}

      <Radar />
      <VoiceControl />
      <DroneStatus />
      <TelemertyPanel />

      {/* TEMP TEST BUTTONS */}
      <button 
        onClick={() => setWarning(true)} 
        style={{ position: "absolute", bottom: 50, right: 10 }}
      >
        Trigger Warning
      </button>

      <button 
        onClick={() => setBlocked("Drone Alpha cannot attack without target!")} 
        style={{ position: "absolute", bottom: 10, right: 10 }}
      >
        Trigger Blocked
      </button>
    </div>
  );
}