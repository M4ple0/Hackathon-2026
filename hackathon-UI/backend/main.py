import logging
from voice_listener import stt_loop
from command_parser import CommandParser
from voice_listener import speak

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

parser = CommandParser()

def handle_command(text:str):
    print("\n New Command Recieved")
    print(f"transcript: {text}")

    commands = parser.parse_compound(text)

    for cmd in commands:
        action = cmd.get("action")
        drone = cmd.get("drone", "-")
        target = cmd.get("target", "-")
        altitude = cmd.get("altitude_m")
        confidence = cmd.get("confidence", 0)

        print(f"action : {action}")
        print(f"drone : {drone}")
        print(f"confidence : {confidence:.0%}")

        if confidence < 0.4:
            print("parser confidence too low, operator please repeat")
            speak("command unclear. Please repeat")
            continue
    #placeholder for saftey engine
        print(f"send to saftey engine")

if __name__ == "__main__":
    print("system starting...")
    print("say a wake word to begin. say 'deactivate' to stop\n")
    stt_loop(on_command=handle_command)