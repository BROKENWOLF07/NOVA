
import speech_recognition as sr
import pyttsx3
import threading
import time

# ---------------------------------------------------------
# NOVA - improved speech recognition and text-to-speech
# ---------------------------------------------------------

recognizer = sr.Recognizer()

# Give the microphone more time to capture complete sentences.
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 180
recognizer.dynamic_energy_adjustment_damping = 0.12
recognizer.dynamic_energy_ratio = 1.25

# Wait longer for natural pauses between words.
recognizer.pause_threshold = 1.0
recognizer.phrase_threshold = 0.2
recognizer.non_speaking_duration = 0.5

speech_lock = threading.Lock()
microphone_lock = threading.Lock()

engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)

_calibrated = False
_microphone_device_index = None


def speak(text):
    """Speak text safely without crashing NOVA."""
    if text is None or not str(text).strip():
        return

    try:
        with speech_lock:
            engine.say(str(text))
            engine.runAndWait()
    except Exception as exc:
        print(f"[NOVA TTS ERROR] {exc}")


def calibrate_microphone(force=False):
    """
    Calibrate once at startup instead of recalibrating for every command.
    Run this again if the microphone or room noise changes significantly.
    """
    global _calibrated

    if _calibrated and not force:
        return True

    try:
        with microphone_lock:
            with sr.Microphone(device_index=_microphone_device_index) as source:
                print("[NOVA] Calibrating microphone. Please stay quiet...")
                recognizer.adjust_for_ambient_noise(source, duration=1.2)

        # Avoid an excessively high threshold in a quiet room.
        recognizer.energy_threshold = max(
            100, min(recognizer.energy_threshold, 500)
        )

        _calibrated = True
        print(
            f"[NOVA] Microphone ready. Energy threshold: "
            f"{recognizer.energy_threshold:.0f}"
        )
        return True

    except Exception as exc:
        print(f"[NOVA MICROPHONE ERROR] {exc}")
        return False


def listen(timeout=4, phrase_time_limit=12):
    """
    Listen for speech and return recognized text.

    timeout:
        Seconds to wait for speech to begin.

    phrase_time_limit:
        Maximum seconds allowed for one spoken phrase.
    """
    try:
        with microphone_lock:
            with sr.Microphone(
                device_index=_microphone_device_index
            ) as source:

                # Calibrate only on the first successful microphone opening.
                global _calibrated
                if not _calibrated:
                    print("[NOVA] Calibrating microphone...")
                    recognizer.adjust_for_ambient_noise(
                        source, duration=1.0
                    )
                    recognizer.energy_threshold = max(
                        100, min(recognizer.energy_threshold, 500)
                    )
                    _calibrated = True

                print("[NOVA] Listening...")

                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

        # Process the recording after releasing the microphone.
        print("[NOVA] Processing speech...")

        # Indian English is the default for this assistant.
        try:
            text = recognizer.recognize_google(
                audio,
                language="en-IN"
            )
        except sr.UnknownValueError:
            # Retry once using a broader English language setting.
            try:
                text = recognizer.recognize_google(
                    audio,
                    language="en-US"
                )
            except sr.UnknownValueError:
                print("[NOVA] I couldn't make out that recording. Please try again.")
                return None

        text = text.strip()

        if text:
            print(f"[YOU] {text}")
            return text

        return None

    except sr.WaitTimeoutError:
        # Normal when waiting for the wake word. No error needed.
        return None

    except sr.UnknownValueError:
        print("[NOVA] Speech was unclear. Please try once more.")
        return None

    except sr.RequestError as exc:
        print(
            "[NOVA NETWORK ERROR] Speech recognition could not reach "
            f"the service: {exc}"
        )
        return None

    except OSError as exc:
        print(
            f"[NOVA MICROPHONE ERROR] {exc}. Check your Windows input device."
        )
        return None

    except Exception as exc:
        print(f"[NOVA SPEECH ERROR] {exc}")
        time.sleep(0.2)
        return None


def reset_microphone():
    """Recalibrate after changing microphones or moving to a noisy room."""
    global _calibrated
    _calibrated = False
    return calibrate_microphone(force=True)


def set_microphone_device(device_index=None):
    """
    Optionally select a specific microphone by its device index.
    Use None for the Windows default microphone.
    """
    global _microphone_device_index, _calibrated
    _microphone_device_index = device_index
    _calibrated = False
    return calibrate_microphone(force=True)
