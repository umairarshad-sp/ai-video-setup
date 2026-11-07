"""Original music and sound effects, synthesized in code, and the final mix.

Everything is generated from numbers (no samples, no downloads), so there are no
licensing questions. Sample rate 48 kHz, float32, mono.

    music_mystery(seconds, bpm=92, seed=1)   a sneaky detective loop in D minor
    sfx(name)                                sting, reveal, tick, whoosh, stamp, pop, riser, boing
    mix(voice, voice_sr, music, events, out_wav)   ducking + loudness to -14 LUFS
"""
import os, subprocess, tempfile
import numpy as np
import soundfile as sf

SR = 48000
rng0 = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.2, total=None):
    total = total or n / SR
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), 1.0)
    e = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / max(d, 1e-6), e)
    e = np.where(t >= a + d, s, e)
    rel = total - r
    e = np.where(t > rel, e * np.clip(1 - (t - rel) / max(r, 1e-6), 0, 1), e)
    return e


def lowpass(x, cutoff):
    """one-pole low-pass (cheap, smooth)"""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # fine for short sounds; music uses fft_lowpass
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x)).astype(np.float32)


def note_hz(n):
    """MIDI note number -> Hz"""
    return 440.0 * 2 ** ((n - 69) / 12)


def pluck(freq, sec, bright=0.5, seed=0):
    """Karplus-Strong plucked string (pizzicato bass / guitar)"""
    n = int(sec * SR)
    p = max(int(SR / freq), 2)
    r = np.random.default_rng(seed)
    buf = r.uniform(-1, 1, p).astype(np.float32)
    buf = fft_filter(np.tile(buf, 4), hi=2000 + 6000 * bright)[:p]
    out = np.empty(n, np.float32)
    decay = 0.996
    for i in range(n):
        v = buf[i % p]
        nxt = buf[(i + 1) % p]
        buf[i % p] = decay * 0.5 * (v + nxt)
        out[i] = v
    return out * env_adsr(n, a=0.002, d=0.05, s=1.0, r=0.06)


def vibe(freq, sec):
    """vibraphone-ish bell: sine + 4th harmonic, tremolo, long decay"""
    t = t_axis(sec)
    trem = 1 + 0.25 * np.sin(2 * np.pi * 5.2 * t)
    x = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t * 9)
    return (x * np.exp(-t * 2.2) * trem).astype(np.float32)


def pad_chord(notes, sec):
    t = t_axis(sec)
    x = np.zeros_like(t)
    for n in notes:
        f = note_hz(n)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            x += np.sin(2 * np.pi * ff * t) + 0.3 * np.sin(2 * np.pi * 2 * ff * t) + 0.12 * np.sin(2 * np.pi * 3 * ff * t)
    x /= len(notes) * 3
    e = np.minimum(t / 0.6, 1) * np.minimum((sec - t) / 0.4, 1)
    return (x * np.clip(e, 0, 1)).astype(np.float32)


def noise_hit(sec, lo, hi, decay, seed=0):
    r = np.random.default_rng(seed)
    x = r.uniform(-1, 1, int(sec * SR)).astype(np.float32)
    x = fft_filter(x, lo=lo, hi=hi)
    t = t_axis(sec)
    return x * np.exp(-t * decay)


def place(dst, src, at, gain=1.0):
    i = int(at * SR)
    if i >= len(dst):
        return
    j = min(len(dst), i + len(src))
    dst[i:j] += gain * src[: j - i]


# ---------------------------------------------------------------- music
def music_mystery(seconds, bpm=92, seed=1, intensity=1.0):
    """A sneaky detective loop: pizzicato walking bass, soft pad, vibraphone motif,
    brushed off-beat hats and finger snaps on 2 and 4. D minor, i - VI - iv - V."""
    beat = 60 / bpm
    bar = 4 * beat
    n_bars = int(np.ceil(seconds / bar)) + 1
    out = np.zeros(int(n_bars * bar * SR) + SR, np.float32)
    prog = [(50, [62, 65, 69]), (46, [58, 62, 65]), (43, [55, 58, 62]), (45, [57, 61, 64])]  # Dm Bb Gm A
    walks = [[0, 7, 12, 10], [0, 7, 10, 7], [0, 3, 7, 5], [0, 7, 4, 1]]
    motif = [(0.5, 74), (1.0, 77), (1.5, 76), (2.5, 74), (3.0, 73)]  # (beat, note), answered differently each 2 bars
    motif2 = [(0.5, 69), (1.5, 70), (2.0, 69), (3.0, 65)]
    r = np.random.default_rng(seed)
    for b in range(n_bars):
        root, chord = prog[b % 4]
        t0 = b * bar
        # bass: walking quarter notes, plucked
        for k, iv in enumerate(walks[b % 4]):
            place(out, pluck(note_hz(root - 12 + iv), beat * 0.95, bright=0.35, seed=b * 4 + k), t0 + k * beat, 0.55)
        # pad
        place(out, pad_chord(chord, bar * 1.02), t0, 0.10 * intensity)
        # vibraphone motif every other bar, an answer phrase in between
        mot = motif if b % 2 == 0 else motif2
        if b % 8 not in (6, 7) or intensity > 0.8:
            for beat_pos, n in mot:
                place(out, vibe(note_hz(n), 1.4), t0 + beat_pos * beat, 0.11)
        # hats on the off-beats, snaps on 2 and 4
        for k in range(4):
            place(out, noise_hit(0.05, 6000, 14000, 60, seed=b * 8 + k), t0 + (k + 0.5) * beat, 0.05 * intensity)
            if k in (1, 3):
                place(out, noise_hit(0.08, 1200, 5000, 45, seed=b * 9 + k), t0 + k * beat, 0.16 * intensity)
    out = out[: int(seconds * SR)]
    fade = int(1.2 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return out / (np.max(np.abs(out)) + 1e-9) * 0.7


# ---------------------------------------------------------------- sfx
def sfx(name):
    if name == "sting":  # dun-dun-DUN
        out = np.zeros(int(2.4 * SR), np.float32)
        for at, notes, g in [(0.0, [38, 50, 53], 0.6), (0.22, [37, 49, 52], 0.6), (0.48, [38, 50, 53, 57], 1.0)]:
            dur = 0.2 if g < 1 else 1.8
            t = t_axis(dur)
            x = np.zeros_like(t)
            for n in notes:
                f = note_hz(n)
                x += sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 8))  # brassy saw
            x *= np.exp(-t * (3 if g == 1 else 8)) / len(notes)
            place(out, fft_filter(x.astype(np.float32), hi=2500), at, g)
            boom = np.sin(2 * np.pi * 55 * t * np.exp(-t * 2)) * np.exp(-t * 4)
            place(out, boom.astype(np.float32), at, 0.8 * g)
        return out / np.max(np.abs(out))
    if name == "reveal":  # bright major hit with a cymbal swell
        t = t_axis(2.2)
        x = np.zeros_like(t)
        for n in (62, 66, 69, 74, 78):
            f = note_hz(n)
            x += (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 1.6)
        cym = noise_hit(2.2, 4000, 16000, 2.2, seed=3)
        boom = np.sin(2 * np.pi * 60 * t * np.exp(-t * 3)) * np.exp(-t * 5)
        out = x / 5 + 0.5 * cym + 0.9 * boom
        return (out / np.max(np.abs(out))).astype(np.float32)
    if name == "tick":  # woodblock
        t = t_axis(0.09)
        x = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 70) + 0.4 * np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 110)
        return (x / np.max(np.abs(x))).astype(np.float32)
    if name == "whoosh":
        sec = 0.45
        t = t_axis(sec)
        r = np.random.default_rng(5)
        x = r.uniform(-1, 1, len(t)).astype(np.float32)
        # sweep a band upward by mixing three bands with moving gains
        bands = [fft_filter(x, lo=lo, hi=lo * 2.5) for lo in (300, 900, 2700)]
        p = t / sec
        g = [np.clip(1 - 3 * np.abs(p - c), 0, 1) for c in (0.2, 0.5, 0.8)]
        out = sum(b * gg for b, gg in zip(bands, g)) * np.sin(np.pi * p) ** 1.5
        return (out / np.max(np.abs(out))).astype(np.float32)
    if name == "stamp":
        t = t_axis(0.5)
        thump = np.sin(2 * np.pi * 70 * t * np.exp(-t * 6)) * np.exp(-t * 14)
        slap = noise_hit(0.5, 400, 5000, 35, seed=9)
        out = thump + 0.7 * slap
        return (out / np.max(np.abs(out))).astype(np.float32)
    if name == "pop":
        t = t_axis(0.12)
        f = 600 + 1400 * (t / 0.12)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
        return (x / np.max(np.abs(x))).astype(np.float32)
    if name == "riser":
        sec = 1.6
        t = t_axis(sec)
        f = 200 * 2 ** (2.5 * t / sec)
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
        nz = fft_filter(np.random.default_rng(2).uniform(-1, 1, len(t)).astype(np.float32), lo=2000)
        out = (0.5 * tone + 0.5 * nz) * (t / sec) ** 2
        return (out / np.max(np.abs(out))).astype(np.float32)
    if name == "boing":  # comedy, for Barnaby's wrong guesses
        t = t_axis(0.5)
        f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
        return (x / np.max(np.abs(x))).astype(np.float32)
    raise ValueError(f"unknown sfx {name}")


SFX_GAIN = {"sting": 0.8, "reveal": 0.85, "tick": 0.35, "whoosh": 0.35, "stamp": 0.8, "pop": 0.3,
            "riser": 0.45, "boing": 0.5}


# ---------------------------------------------------------------- mix
def resample(x, sr_from, sr_to=SR):
    if sr_from == sr_to:
        return x.astype(np.float32)
    from scipy.signal import resample_poly
    g = np.gcd(sr_from, sr_to)
    return resample_poly(x, sr_to // g, sr_from // g).astype(np.float32)


def duck_gain(voice, floor_db=-11.0, attack=0.04, release=0.35):
    """1.0 where nobody speaks, down to floor_db under speech, smoothed"""
    win = int(0.02 * SR)
    env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, "same"))
    speaking = (env > 0.02).astype(np.float32)
    g_low = 10 ** (floor_db / 20)
    target = 1 - (1 - g_low) * speaking
    out = np.empty_like(target)
    a_up = np.exp(-1 / (release * SR))
    a_dn = np.exp(-1 / (attack * SR))
    acc = 1.0
    # vectorised enough: process in blocks of 1 ms
    step = 48
    for i in range(0, len(target), step):
        tv = target[i]
        a = a_dn if tv < acc else a_up
        acc = a ** step * acc + (1 - a ** step) * tv
        out[i:i + step] = acc
    return out


def mix(voice, voice_sr, music, events, out_wav, music_gain=0.55, lufs=-14.0):
    """voice: float array; music: float array at SR; events: [(name, time_s)]"""
    v = resample(voice, voice_sr)
    n = max(len(v), len(music))
    v = np.pad(v, (0, n - len(v)))
    m = np.pad(music, (0, n - len(music)))
    fx = np.zeros(n, np.float32)
    for name, at in events:
        place(fx, sfx(name), at, SFX_GAIN.get(name, 0.5))
    out = v * 1.0 + m * music_gain * duck_gain(v) + fx
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.9
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.wav")
        sf.write(raw, out, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                        f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-ar", str(SR), out_wav], check=True)
    return n / SR


if __name__ == "__main__":
    os.makedirs("work", exist_ok=True)
    sf.write("work/music_test.wav", music_mystery(24), SR)
    for k in SFX_GAIN:
        sf.write(f"work/sfx_{k}.wav", sfx(k), SR)
    print("wrote work/music_test.wav and work/sfx_*.wav")
