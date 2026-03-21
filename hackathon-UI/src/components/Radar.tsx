import "../styles/Radar.css";

export default function Radar() {
  const toPercent = (x, y) => {
    const left = ((x + 60) / 120) * 100;
    const top = ((37 - y) / 74) * 100;
    return { top: `${top}%`, left: `${left}%` };
  };

  const locations = [
    { name: "Landing Pad", x: -40, y: 0 },
    { name: "West Gate", x: -52, y: 0 },
    { name: "NW Tower", x: -52, y: 35 },
    { name: "NE Tower", x: 52, y: 35 },
    { name: "SE Tower", x: 52, y: -35 },
    { name: "SW Tower", x: -52, y: -35 },
    { name: "Command", x: 20, y: 10 },
    { name: "Rooftop", x: 25, y: 14 },
    { name: "Barracks 1", x: -20, y: 25 },
    { name: "Barracks 2", x: -20, y: -25 },
    { name: "Motor Pool", x: 38, y: -20 },
    { name: "Containers", x: 0, y: -15 },
    { name: "Comms Tower", x: 40, y: 30 },
    { name: "Fuel Depot", x: -27, y: -32 },
  ];

  const droneA = { x: -40, y: 0 };
  const droneB = { x: 10, y: 5 };

  return (
    <div className="mapPanel">
      <div className="mapContainer">

        <div
          className="drone droneA"
          style={toPercent(droneA.x, droneA.y)}
        ></div>

        <div
          className="drone droneB"
          style={toPercent(droneB.x, droneB.y)}
        ></div>

        {locations.map((loc) => (
          <div
            key={loc.name}
            className="locationLabel"
            style={toPercent(loc.x, loc.y)}
          >
            {loc.name}
          </div>
        ))}

        <div
          className="noGoZone"
          style={{
            ...toPercent(-27, -32),
            width: "16%",
            height: "16%",
          }}
        ></div>

        <div
          className="noGoZone warning"
          style={{
            ...toPercent(40, 30),
            width: "12%",
            height: "12%",
          }}
        ></div>

      </div>
    </div>
  );
}