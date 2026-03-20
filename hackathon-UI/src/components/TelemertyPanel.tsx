import "../styles/TelemetryPanel.css"

export default function TelemertyPanel() {
    return (
        <div className="telemetryPanel">
            <div className="telemetryItem">
                <span className="label">Position:</span>
                <span className="value">X: 12.3 Y: 45.6 Z: 7.8</span>
            </div>
            <div className="telemetryItem">
                <span className="label">Altitude:</span>
                <span className="value">120 m</span>
            </div>
            <div className="telemetryItem">
                <span className="label">Battery:</span>
                <span className="value">87%</span>
            </div>
            <div className="telemetryItem">
                <span className="label">Mode:</span>
                <span className="value">Auto</span>
            </div>
        </div>
    )
}