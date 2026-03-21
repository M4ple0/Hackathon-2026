import { useState } from "react";
import Radar from "../components/Radar";
import VoiceControl from "../components/VoiceControl";
import DroneStatus from "../components/DroneStatus";
import TelemertyPanel from "../components/TelemertyPanel";
import "../styles/Dashboard.css";

export default function Dashboard() {
  const [warning, setWarning] = useState(false);

  return (
    <div className={`dashboard ${warning ? "danger-mode" : ""}`}>
      
      {/* 🔥 POPUP */}
      {warning && (
        <div className="warningOverlay">
          <div className="warningPopup">
            <h2>⚠ HIGH RISK ACTION</h2>
            <p>Confirm command execution</p>
            <button onClick={() => setWarning(false)}>Confirm</button>
            <button onClick={() => setWarning(false)}>Cancel</button>
          </div>
        </div>
      )}

      <Radar />
      <VoiceControl />
      <DroneStatus />
      <TelemertyPanel />

      {/* TEMP TEST BUTTON */}
      <button 
        onClick={() => setWarning(true)} 
        style={{ position: "absolute", bottom: 10, right: 10 }}
      >
        Trigger Warning
      </button>
    </div>
  );
}