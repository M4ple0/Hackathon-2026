import "../styles/DroneStatus.css"

export default function DroneStatus() {
  return (
    <div className="status">
        <div className="terminalContent">
            <p>Initializing systems...</p>
            <p>Drone connection established.</p>
            <p>Listening for commands...</p>
        </div>
    </div>
  )
}