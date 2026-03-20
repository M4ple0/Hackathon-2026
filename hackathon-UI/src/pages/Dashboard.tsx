import Radar from "../components/Radar";
import VoiceControl from "../components/VoiceControl";
import DroneStatus from "../components/DroneStatus";
import "../styles/dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <Radar />
      <VoiceControl />
      <DroneStatus />
    </div>
  );
}