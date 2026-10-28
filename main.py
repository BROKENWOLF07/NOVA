from speech import speak, listen
from brain import ask_ai
from commands import run_command
from datetime import datetime
import pyautogui

WAKE_WORD = "nova"


def main():

    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good morning sir"

    elif hour < 18:
        greeting = "Good afternoon sir"

    else:
        greeting = "Good evening sir"

    speak(
        f"{greeting}. "
        f"Nova systems online. "
        f"All systems are functioning normally. "
        f"Say Nova to wake me."
    )

    while True:

        print("Waiting for wake word...")

        wake = listen()

        if not wake:
            continue

        wake = wake.lower().strip()

        print("Heard:", wake)

        if WAKE_WORD in wake:

            speak("Yes sir")

            while True:

                command = listen()

                if not command:
                    continue

                command = command.lower().strip()

                print("Command:", command)

                if (
                    "sleep" in command
                    or "go to sleep" in command
                    or "stop listening" in command
                    or "bye nova" in command
                    or "goodbye" in command
                ):

                    speak("Entering standby mode sir")
                    break

                # CLOSE CURRENT WINDOW
                if (
                    "close current window" in command
                    or "close this window" in command
                    or "close current app" in command
                ):
                    speak("Closing the current window sir")
                    pyautogui.hotkey("alt", "f4")
                    continue

                response = run_command(command)

                if response == "I did not understand that command sir":

                    response = ask_ai(command)

                print("Response:", response)

                speak(response)


if __name__ == "__main__":
    main()