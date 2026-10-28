import pyautogui
import time
import re


# -------------------------------------------------
# BASIC VIDEO CONTROLS
# -------------------------------------------------

def stop_video():
    """Pause the current video."""
    pyautogui.press("space")
    return "Video paused sir"


def play_video():
    """Resume the current video."""
    pyautogui.press("space")
    return "Video resumed sir"


def mute_video():
    """Mute the current video."""
    pyautogui.press("m")
    return "Video muted sir"


def unmute_video():
    """Unmute the current video."""
    pyautogui.press("m")
    return "Video unmuted sir"


def next_video():
    """Play the next video."""
    pyautogui.hotkey("shift", "n")
    return "Playing next video sir"


def previous_video():
    """Play the previous video."""
    pyautogui.hotkey("shift", "p")
    return "Playing previous video sir"


def fullscreen_video():
    """Enter fullscreen."""
    pyautogui.press("f")
    return "Entering fullscreen sir"


def exit_fullscreen():
    """Exit fullscreen."""
    pyautogui.press("f")
    return "Exiting fullscreen sir"


# -------------------------------------------------
# FORWARD VIDEO
# -------------------------------------------------

def forward_video(seconds=10):
    """
    Forward YouTube video by the requested number of seconds.

    YouTube's right arrow moves approximately 5 seconds.
    NOVA presses the right arrow the required number of times.
    """

    try:
        seconds = int(seconds)

        if seconds <= 0:
            return "Please give me a valid number of seconds sir"

        # YouTube right arrow ≈ 5 seconds
        presses = max(1, round(seconds / 5))

        for _ in range(presses):
            pyautogui.press("right")
            time.sleep(0.05)

        actual_seconds = presses * 5

        return f"Forwarded video by {actual_seconds} seconds sir"

    except Exception:
        return "I could not forward the video sir"


# -------------------------------------------------
# REWIND VIDEO
# -------------------------------------------------

def rewind_video(seconds=10):
    """
    Rewind YouTube video by the requested number of seconds.

    YouTube's left arrow moves approximately 5 seconds.
    NOVA presses the left arrow the required number of times.
    """

    try:
        seconds = int(seconds)

        if seconds <= 0:
            return "Please give me a valid number of seconds sir"

        # YouTube left arrow ≈ 5 seconds
        presses = max(1, round(seconds / 5))

        for _ in range(presses):
            pyautogui.press("left")
            time.sleep(0.05)

        actual_seconds = presses * 5

        return f"Rewound video by {actual_seconds} seconds sir"

    except Exception:
        return "I could not rewind the video sir"