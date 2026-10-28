import os
import webbrowser
import psutil
from datetime import datetime

from memory import save_memory, get_memory
from weather import get_weather
from news import get_news

from volume import (
    volume_up,
    volume_down,
    mute_volume,
    set_volume
)

from brightness import (
    brightness_up,
    brightness_down,
    set_brightness,
    get_brightness
)

from media_control import (
    stop_video,
    play_video,
    mute_video,
    unmute_video,
    next_video,
    previous_video,
    fullscreen_video,
    exit_fullscreen,
    forward_video,
    rewind_video
)

from whatsapp import (
    open_whatsapp,
    search_contact,
    call_contact,
    video_call_contact,
    type_message,
    send_message,
    send_whatsapp_message
)

# ---------------- CLOSE APPLICATION ----------------

APP_PROCESS_NAMES = {
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "microsoft edge": ["msedge.exe"],
    "brave": ["brave.exe"],
    "firefox": ["firefox.exe"],
    "vs code": ["code.exe"],
    "visual studio code": ["code.exe"],
    "vscode": ["code.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["CalculatorApp.exe", "calc.exe"],
    "calc": ["CalculatorApp.exe", "calc.exe"],
    "paint": ["mspaint.exe"],
    "file explorer": ["explorer.exe"],
    "explorer": ["explorer.exe"],
    "whatsapp": ["WhatsApp.exe"],
    "discord": ["Discord.exe"],
    "spotify": ["Spotify.exe"],
}

def close_application(app_name):
    """Close a known Windows application."""
    app_name = app_name.lower().strip()

    if not app_name:
        return "Please tell me which application to close sir"

    process_names = APP_PROCESS_NAMES.get(app_name)

    if not process_names:
        return (
            f"I do not have a close command configured for {app_name} yet sir. "
            "You can add it to APP_PROCESS_NAMES."
        )

    closed = False

    for process in psutil.process_iter(["name"]):
        try:
            process_name = process.info["name"]

            if process_name and process_name.lower() in process_names:
                process.terminate()
                closed = True

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if closed:
        return f"Closing {app_name} sir"

    return f"{app_name} is not currently running sir"


def run_command(command):
    print("COMMAND RECEIVED:", command)

    command = command.lower().strip()



    # VOLUME UP
    if "volume up" in command:
        return volume_up()

    # VOLUME DOWN
    elif "volume down" in command:
        return volume_down()

    # MUTE
    elif "mute" in command:
        return mute_volume()

    # SET VOLUME
    elif command.startswith("set volume"):
        try:
            percent = int(
                command.replace("set volume", "").strip()
            )
            return set_volume(percent)

        except:
            return "Please tell me a valid volume percentage sir"

    # TIME
    elif "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The time is {current_time} sir"

    # DATE
    elif "date" in command:
        current_date = datetime.now().strftime("%d %B %Y")
        return f"Today is {current_date} sir"


    # BATTERY
    elif "battery" in command:
        battery = psutil.sensors_battery()

        if battery:
            return f"Battery level is {battery.percent} percent sir"

        return "Battery information unavailable sir"

    # WEATHER
    elif "weather in" in command:

        city = command.replace("weather in", "").strip()

        return get_weather(city)

    elif command == "weather":

        return get_weather("Chennai")

    # NEWS
    elif "latest news" in command or command == "news":

        return get_news()

    # CLOSE APPLICATION
    elif command.startswith("close "):
        app_name = command.replace("close ", "", 1).strip()

        if app_name in ("computer", "system", "nova", "yourself"):
            return "I will remain ready for your next command sir"

        return close_application(app_name)

    # OPEN GOOGLE
    elif "open google" in command:

        webbrowser.open("https://www.google.com")

        return "Opening Google sir"

    # OPEN YOUTUBE
    elif "open youtube" in command:

        webbrowser.open("https://www.youtube.com")

        return "Opening YouTube sir"

    # PLAY ON YOUTUBE
    elif command.startswith("play "):

        import pywhatkit

        song = command.replace("play ", "").strip()

        pywhatkit.playonyt(song)

        return f"Playing {song} on YouTube sir"

    # OPEN CHROME
    elif "open chrome" in command:

        os.system("start chrome")

        return "Opening Chrome sir"

    # OPEN EXPLORER
    elif "open explorer" in command or "open file explorer" in command:

        os.system("explorer")

        return "Opening File Explorer sir"

    # OPEN SETTINGS
    elif "open settings" in command:

        os.system("start ms-settings:")

        return "Opening Settings sir"

    # GOOGLE SEARCH
    elif command.startswith("search "):

        query = command.replace("search", "").strip()

        webbrowser.open(
            f"https://www.google.com/search?q={query}"
        )

        return f"Searching for {query} sir"

    # PLAY MUSIC
    elif "play music" in command:

        music_folder = r"C:\Users\kavit\Music"

        try:
            os.startfile(music_folder)

            return "Opening music folder sir"

        except:
            return "Music folder not found sir"

    # SHUTDOWN
    elif "shutdown computer" in command or "shutdown system" in command:

        os.system("shutdown /s /t 10")

        return "Shutting down computer in 10 seconds sir"

    # RESTART
    elif "restart computer" in command or "restart system" in command:

        os.system("shutdown /r /t 10")

        return "Restarting computer in 10 seconds sir"

    # CANCEL SHUTDOWN
    elif "cancel shutdown" in command:

        os.system("shutdown /a")

        return "Shutdown cancelled sir"



    # BRIGHTNESS UP
    elif "brightness up" in command:
        return brightness_up()

    # BRIGHTNESS DOWN
    elif "brightness down" in command:
        return brightness_down()

    # BRIGHTNESS LEVEL
    elif "brightness level" in command:
        return get_brightness()

    # SET BRIGHTNESS
    elif command.startswith("set brightness"):

        try:
            percent = command.replace(
                "set brightness",
                ""
            ).strip()

            return set_brightness(percent)

        except:
            return "Please tell me a valid brightness percentage sir"

    # NOTEPAD
    elif "open notepad" in command:

        os.system("notepad")

        return "Opening Notepad sir"

    # CALCULATOR
    elif "open calculator" in command:

        os.system("calc")

        return "Opening Calculator sir"

    # PAINT
    elif "open paint" in command:

        os.system("mspaint")

        return "Opening Paint sir"

    # SAVE NAME
    elif "my name is" in command:

        name = command.replace("my name is", "").strip()

        save_memory("name", name)

        return f"Nice to meet you {name} sir"

    # RECALL NAME
    elif "what is my name" in command:

        name = get_memory("name")

        if name:
            return f"Your name is {name} sir"

        return "I do not know your name yet sir"

    # VIDEO CONTROLS

    elif "stop video" in command:
        return stop_video()

    elif "pause video" in command:
        return stop_video()

    elif "play video" in command:
        return play_video()

    elif "resume video" in command:
        return play_video()

    elif "mute video" in command:
        return mute_video()

    elif "unmute video" in command:
        return unmute_video()

    elif "next video" in command:
        return next_video()

    elif "previous video" in command:
        return previous_video()

    elif "fullscreen video" in command:
        return fullscreen_video()

    elif "exit fullscreen" in command:
        return exit_fullscreen()

    elif "forward video" in command:
        return forward_video()

    elif "rewind video" in command:
        return rewind_video()

    # WHATSAPP COMMANDS
        # ---------------- WHATSAPP ----------------

    elif "open whatsapp" in command:

        return open_whatsapp()

    elif command.startswith("open chat"):

        contact = command.replace("open chat", "").strip()

        return search_contact(contact)

    elif command.startswith("call"):

        contact = command.replace("call", "").strip()

        search_contact(contact)

        return call_contact()

    elif command.startswith("video call"):

        contact = command.replace("video call", "").strip()

        search_contact(contact)

        return video_call_contact()

    elif command.startswith("type message"):

        message = command.replace("type message", "").strip()

        return type_message(message)

    elif command == "send message":

        return send_message()

    elif command.startswith("send whatsapp"):

        try:

            parts = command.replace(
                "send whatsapp",
                ""
            ).strip().split(",", 1)

            phone = parts[0].strip()

            message = parts[1].strip()

            return send_whatsapp_message(
                phone,
                message
            )

        except:

            return (
                "Please say the phone number "
                "and message correctly sir"
            )
    

    else:

        return "I did not understand that command sir"
    