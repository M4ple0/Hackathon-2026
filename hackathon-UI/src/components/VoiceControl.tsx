import { useState, useEffect } from "react";
import "../styles/VoiceControl.css";
import "../styles/VoiceControlAnimation.css";

export default function VoiceControl() {
    const [isSpeaking, setIsSpeaking] = useState(false);

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch("http://localhost:8000/voice-status");
                const data = await res.json();
                setIsSpeaking(data.listening);
            } catch (err) {
                console.error(err);
            }
        }, 150);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="voiceControl">
            <div className={`circle ${isSpeaking ? "speaking" : ""}`} />
        </div>
    );
}