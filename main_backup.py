from speech import speak, listen
from brain import ask_ai
from commands import run_command

WAKE_WORD = "nova"


def assistant_mode():

    speak("Listening")

    while True:

        command = listen()

        if not command:
            continue

        command = command.lower()

        print("Command received:", command)

        if "sleep" in command:
            speak("Going to sleep")
            break

        response = run_command(command)

        if response:

            print(response)
            speak(response)

        else:

            response = ask_ai(command)

            print(response)
            speak(response)


def main():

    speak("Nova is online")

    while True:

        print("Waiting for wake word...")

        wake = listen()

        if not wake:
            continue

        wake = wake.lower()

        if WAKE_WORD in wake:

            assistant_mode()


if __name__ == "__main__":
    main()