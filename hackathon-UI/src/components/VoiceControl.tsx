import "../styles/VoiceControl.css"
import "../styles/VoiceControlAnimation.css"
import { useState } from "react";

export default function VoiceControl() {
    const [isSpeaking, setIsSpeaking] = useState(true);

    return (
     <div className="voiceControl">
        <div 
            className={`circle ${isSpeaking ? "speaking" : ""}`}
            >
        </div>
    </div>
    )
}