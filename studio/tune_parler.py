"""Find the steadiest Indic Parler-TTS voice for a character.

    .venv-parler/bin/python studio/tune_parler.py rafiq jamil

For each candidate (description x seed) it speaks the same test sentences, then scores:
  pitch spread   max/min of the per-sentence median pitch (lower = steadier)
  timbre spread  mean distance between the sentences' average log-mel spectra
  pitch drift    distance from the approved audition clip's pitch
Writes work/tune/<id>/<cand>_<seed>_<n>.wav and prints a ranking.
"""
import json, os, sys, time
import numpy as np
import soundfile as sf
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "ai4bharat/indic-parler-tts"
TAIL = "The recording is very clear, close-sounding, with no background noise."
SEEDS = [1001, 7, 42]
SENTENCES = ["आज इतवार है, और यहाँ कोई झूठ बोल रहा है।", "मुझे कुछ नहीं पता, मैं तो बस यहाँ खड़ा था!"]

CANDIDATES = {
    "rafiq": {
        "orig": "Rohit speaks in a loud, deep, dramatic voice with a low pitch at a moderate pace, very expressive.",
        "steady": "Rohit speaks in a loud, deep voice with a low pitch at a moderate pace, slightly expressive, with a steady and consistent tone.",
        "flat": "Rohit speaks in a deep, booming voice with a low pitch at a moderate pace, with very little variation in tone.",
    },
    "jamil": {
        "orig": "Rohit speaks in a very low-pitched, gruff and grumpy voice of an old man at a slow pace, expressive.",
        "steady": "Rohit speaks in a very low-pitched, gruff and grumpy old man's voice at a slow pace, slightly expressive, with a steady and consistent tone.",
        "flat": "Rohit speaks in a gruff, low-pitched old man's voice at a slow, steady pace, with very little variation in tone.",
    },
}


def f0_median(x, sr):
    x = x[:: max(1, sr // 22050)]
    sr = sr // max(1, sr // 22050)
    fr, hop, out = int(0.04 * sr), int(0.01 * sr), []
    for i in range(0, len(x) - fr, hop):
        s = x[i:i + fr]
        if np.sqrt((s ** 2).mean()) < 0.01:
            continue
        s = s - s.mean()
        c = np.correlate(s, s, "full")[fr - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + np.argmax(c[lo:hi])
        if c[k] > 0.3 * c[0]:
            out.append(sr / k)
    return float(np.median(out)) if out else 0.0


def logmel(x, sr, n=40):
    """average log-mel spectrum of the voiced frames: a simple voice-texture fingerprint"""
    fr, hop = 2048, 512
    frames = [x[i:i + fr] * np.hanning(fr) for i in range(0, len(x) - fr, hop) if np.sqrt((x[i:i + fr] ** 2).mean()) > 0.01]
    if not frames:
        return np.zeros(n)
    spec = np.abs(np.fft.rfft(np.array(frames), axis=1)) ** 2
    freqs = np.fft.rfftfreq(fr, 1 / sr)
    mel = lambda f: 2595 * np.log10(1 + f / 700)  # noqa: E731
    edges = np.linspace(mel(80), mel(8000), n + 2)
    hz = 700 * (10 ** (edges / 2595) - 1)
    fb = np.zeros((n, len(freqs)))
    for i in range(n):
        lo, c, hi = hz[i], hz[i + 1], hz[i + 2]
        fb[i] = np.clip(np.minimum((freqs - lo) / (c - lo), (hi - freqs) / (hi - c)), 0, None)
    m = np.log(spec @ fb.T + 1e-9).mean(axis=0)
    return m - m.mean()


def main():
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    tok = os.environ.get("HF_TOKEN")
    torch.set_num_threads(os.cpu_count() or 4)
    model = ParlerTTSForConditionalGeneration.from_pretrained(REPO, token=tok).eval()
    tokenizer = AutoTokenizer.from_pretrained(REPO, token=tok)
    desc_tok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path, token=tok)
    sr = model.config.sampling_rate
    for cid in sys.argv[1:]:
        prof = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))
        lines = [prof["catchphrase_say"]] + SENTENCES
        ref, rsr = sf.read(os.path.join(ROOT, "work", "audition", "parler", f"{cid}_1.wav"))
        target = f0_median(ref, rsr)
        out_dir = os.path.join(ROOT, "work", "tune", cid)
        os.makedirs(out_dir, exist_ok=True)
        rows = []
        for name, desc in CANDIDATES[cid].items():
            for seed in SEEDS:
                pitches, mels = [], []
                for n, line in enumerate(lines):
                    p = os.path.join(out_dir, f"{name}_{seed}_{n}.wav")
                    if not os.path.exists(p):
                        torch.manual_seed(seed)
                        d = desc_tok(f"{desc} {TAIL}", return_tensors="pt")
                        pr = tokenizer(line, return_tensors="pt")
                        with torch.no_grad():
                            g = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                               prompt_input_ids=pr.input_ids, prompt_attention_mask=pr.attention_mask)
                        sf.write(p, g.cpu().numpy().squeeze(), sr)
                    a, _ = sf.read(p)
                    pitches.append(f0_median(a, sr))
                    mels.append(logmel(a, sr))
                spread = (max(pitches) / max(min(pitches), 1) - 1) * 100
                timbre = float(np.mean([np.linalg.norm(mels[i] - mels[j]) for i in range(3) for j in range(i + 1, 3)]))
                drift = abs(np.median(pitches) / target - 1) * 100
                rows.append((name, seed, spread, timbre, drift, [round(x) for x in pitches]))
                print(f"{cid} {name:6s} seed {seed:5d}  pitch spread {spread:4.0f}%  timbre {timbre:5.2f}  "
                      f"drift from pick {drift:3.0f}%  pitches {[round(x) for x in pitches]}", flush=True)
        json.dump({"target_pitch": target, "rows": rows}, open(os.path.join(out_dir, "scores.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
