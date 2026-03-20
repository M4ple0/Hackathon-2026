import "../styles/Radar.css";

export default function Radar() {
  const locations = [
    { label: "A", top: "15%", left: "20%" },
    { label: "B", top: "25%", left: "70%" },
    { label: "C", top: "40%", left: "35%" },
    { label: "D", top: "60%", left: "80%" },
    { label: "E", top: "75%", left: "50%" },
    { label: "F", top: "85%", left: "20%" },
    { label: "G", top: "50%", left: "10%" },
    { label: "H", top: "30%", left: "55%" },
  ];

  return (
    <div className="mapPanel">
      <div className="mapContainer">
        <div className="drone droneA" style={{ top: "50%", left: "50%" }}></div>
        <div className="drone droneB" style={{ top: "30%", left: "70%" }}></div>

        {locations.map((loc) => (
          <div
            key={loc.label}
            className="locationLabel"
            style={{ top: loc.top, left: loc.left }}
          >
            {loc.label}
          </div>
        ))}
      </div>
    </div>
  );
}