"""Writes sounds/boot.wav: the short chime the speaker plays at power-on.

Synthesised here (no sample from elsewhere), so it is under the repo's
licence. Three rising bell notes (E5, G#5, B5), 22.05 kHz mono 16-bit,
with 300 ms of silence in front: the amplifier only comes on 150 ms after
playback starts, so the chime's start isn't cut off.

    python3 scripts/make-boot-sound.py
"""
import math
import struct
import wave
from pathlib import Path

RATE = 22050
LEAD = 0.30       # silence before the first note, s
STEP = 0.14       # gap between note starts, s
RING = 0.9        # how long each note rings, s
PEAK = 0.45       # loudest sample, fraction of full scale
NOTES = [659.26, 830.61, 987.77]  # E5, G#5, B5

length = LEAD + STEP * (len(NOTES) - 1) + RING
samples = [0.0] * int(length * RATE)

for i, freq in enumerate(NOTES):
    start = int((LEAD + i * STEP) * RATE)
    for n in range(int(RING * RATE)):
        t = n / RATE
        attack = min(1.0, t / 0.005)        # 5 ms fade-in, no click
        decay = math.exp(-t * 5.0)
        tail = min(1.0, (RING - t) / 0.05)  # 50 ms fade-out at the end
        # Fundamental plus a quieter octave: a soft bell
        v = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t) * math.exp(-t * 8.0)
        samples[start + n] += v * attack * decay * tail

scale = PEAK / max(abs(s) for s in samples)
out = Path(__file__).resolve().parent.parent / "sounds" / "boot.wav"
with wave.open(str(out), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(b"".join(struct.pack("<h", int(s * scale * 32767)) for s in samples))
print(f"{out}: {len(samples) / RATE:.2f} s, {out.stat().st_size} bytes")
