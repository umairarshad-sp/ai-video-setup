"""Audio -> mouth shapes, one per video frame.

Mouth set (cartoon standard):
  A = closed (M B P)   B = slightly open (most consonants)   C = open wide (E, I)
  D = big open (A)     E = round (O)                          F = pucker (U, W, OO)
  G = teeth on lip (F, V, S)
Returns None for silent frames so the expression's own resting mouth is used.

This is an audio-only estimate (loudness + brightness of the sound). It is not
phoneme-perfect, but for a cartoon at 30 fps it reads as convincing speech.
"""
import numpy as np


def analyse(samples, sr, fps=30):
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    hop = sr / fps
    n = int(len(samples) / hop)
    win = int(hop * 1.5)
    feats = []
    for i in range(n):
        a = int(i * hop)
        seg = samples[a:a + win]
        if len(seg) < 32:
            feats.append((0.0, 0.0, 0.0))
            continue
        rms = float(np.sqrt(np.mean(seg ** 2)))
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        tot = spec.sum() + 1e-9
        centroid = float((spec * freqs).sum() / tot)
        hi = float(spec[freqs > 4000].sum() / tot)  # hiss: s, f, sh
        feats.append((rms, centroid, hi))
    return np.array(feats)


def mouths(samples, sr, fps=30):
    f = analyse(samples, sr, fps)
    if len(f) == 0:
        return []
    rms = f[:, 0]
    loud = np.percentile(rms[rms > 0], 95) if np.any(rms > 0) else 1.0
    e = np.clip(rms / (loud + 1e-9), 0, 1.2)
    out = []
    for i, (energy, (r, cen, hi)) in enumerate(zip(e, f)):
        if energy < 0.07:
            out.append(None)
        elif hi > 0.35 and energy < 0.45:
            out.append("G")
        elif energy < 0.2:
            out.append("B" if i % 5 else "A")
        elif energy < 0.45:
            if cen < 900:
                out.append("F")
            elif cen > 2200:
                out.append("C")
            else:
                out.append("B")
        else:
            if cen < 1100:
                out.append("E")
            elif cen > 2400:
                out.append("C")
            else:
                out.append("D")
    # smoothing: a mouth must hold for at least 2 frames (avoids flicker)
    sm = list(out)
    for i in range(1, len(sm) - 1):
        if sm[i] != sm[i - 1] and sm[i] != sm[i + 1]:
            sm[i] = sm[i - 1]
    # close the lips briefly between words (speech -> silence -> speech gaps)
    for i in range(1, len(sm)):
        if sm[i] is None and sm[i - 1] not in (None, "A"):
            sm[i] = "A"
            if i + 1 < len(sm) and sm[i + 1] is not None:
                pass
    return sm
