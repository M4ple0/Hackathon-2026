import "../styles/Radar.css"

export default function Radar() {
    return (
        <div className="mapPanel">
            <div className="mapContainer">
                <div className="drone" style={{ top: "50%", left: "50%" }}></div>

                {/* Example friendlies */}
                <div className="friendly" style={{ top: "30%", left: "40%" }}></div>
                <div className="friendly" style={{ top: "70%", left: "60%" }}></div>

                {/* Example enemies */}
                <div className="enemy" style={{ top: "50%", left: "20%" }}></div>
                <div className="enemy" style={{ top: "80%", left: "80%" }}></div>
            </div>
        </div>
    )
}