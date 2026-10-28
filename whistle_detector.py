import sounddevice as sd
import numpy as np


def wait_for_whistle():

    samplerate = 16000

    print("Waiting for whistle...")

    while True:

        audio = sd.rec(
            int(0.5 * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        audio = audio.flatten()

        spectrum = np.abs(np.fft.rfft(audio))

        freqs = np.fft.rfftfreq(len(audio), 1 / samplerate)

        peak = freqs[np.argmax(spectrum)]

        # More strict whistle detection
        if 2000 <= peak <= 3000 and np.max(spectrum) > 100:

            print("Whistle detected!")

            return