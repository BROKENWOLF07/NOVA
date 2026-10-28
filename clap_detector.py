import sounddevice as sd
import numpy as np

print("Available microphones:")
print(sd.query_devices())

samplerate = 44100

while True:

    audio = sd.rec(
        int(0.5 * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='float32'
    )

    sd.wait()

    volume = np.max(np.abs(audio))

    print("Volume:", volume)
    