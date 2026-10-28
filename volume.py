import pyautogui


def volume_up():

    for _ in range(5):
        pyautogui.press("volumeup")

    return "Volume increased sir"


def volume_down():

    for _ in range(5):
        pyautogui.press("volumedown")

    return "Volume decreased sir"


def mute_volume():

    pyautogui.press("volumemute")

    return "Volume muted sir"


def set_volume(percent):

    percent = max(0, min(100, int(percent)))

    # First mute volume to minimum
    for _ in range(50):
        pyautogui.press("volumedown")

    # Raise to desired level
    steps = int(percent / 2)

    for _ in range(steps):
        pyautogui.press("volumeup")

    return f"Volume set to {percent} percent sir"