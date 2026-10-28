import time
import pyautogui
import pywhatkit
import subprocess
import pygetwindow as gw


def open_whatsapp():
    try:
        subprocess.Popen(
            "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
            shell=True
        )

        time.sleep(5)

        return "Opening WhatsApp sir"

    except:

        return "Unable to open WhatsApp sir"


def send_whatsapp_message(phone, message):

    try:

        pywhatkit.sendwhatmsg_instantly(
            phone,
            message,
            wait_time=15,
            tab_close=True
        )

        return "Message sent successfully sir"

    except Exception as e:

        return str(e)


def search_contact(contact):

    try:

        windows = gw.getWindowsWithTitle("WhatsApp")

        if windows:

            windows[0].activate()

        time.sleep(2)

        pyautogui.hotkey("ctrl", "f")

        time.sleep(1)

        pyautogui.write(contact, interval=0.05)

        time.sleep(2)

        pyautogui.press("enter")

        return f"Opening {contact} sir"

    except Exception as e:

        return str(e)


def call_contact():

    pyautogui.press("tab", presses=6, interval=0.2)

    pyautogui.press("enter")

    return "Calling contact sir"


def video_call_contact():

    pyautogui.press("tab", presses=7, interval=0.2)

    pyautogui.press("enter")

    return "Starting video call sir"


def type_message(message):

    pyautogui.write(message, interval=0.03)

    return "Message typed sir"


def send_message():

    pyautogui.press("enter")

    return "Message sent sir"