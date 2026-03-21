import "../styles/TelemetryPanel.css";

type DroneTelemetry = {
  name: string;
  position: { x: number; y: number; z: number };
  altitude: string;
  battery: string;
  mode: string;
};

export default function TelemetryPanel() {
  const drones: DroneTelemetry[] = [
    {
      name: "Drone Alpha",
      position: { x: 12.3, y: 45.6, z: 7.8 },
      altitude: "120 m",
      battery: "87%",
      mode: "Auto",
    },
    {
      name: "Drone Bravo",
      position: { x: 22.1, y: 30.4, z: 5.2 },
      altitude: "95 m",
      battery: "64%",
      mode: "Manual",
    },
  ];

  return (
    <div className="telemetryPanel">
      {drones.map((drone, i) => (
        <div className="droneCard" key={i}>
          <h3 className="droneTitle">{drone.name}</h3>

          <div className="telemetryItem">
            <span className="label">Position:</span>
            <div className="positionValues">
              <span>X: {drone.position.x}</span>
              <span>Y: {drone.position.y}</span>
              <span>Z: {drone.position.z}</span>
            </div>
          </div>

          <div className="telemetryItem">
            <span className="label">Altitude:</span>
            <span className="value">{drone.altitude}</span>
          </div>

          <div className="telemetryItem">
            <span className="label">Battery:</span>
            <span className="value">{drone.battery}</span>
          </div>

          <div className="telemetryItem">
            <span className="label">Mode:</span>
            <span className="value">{drone.mode}</span>
          </div>
        </div>
      ))}
    </div>
  );
}