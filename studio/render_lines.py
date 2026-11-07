"""Render every spoken line of one or more episodes with each character's LOCKED voice.

    .venv-parler/bin/python studio/render_lines.py episodes/s001_part1.json episodes/s001_part2.json

Voices come from cast/<id>/profile.json -> "voice" (approved by the owner; do not change them):
  engine "elevenlabs"        ElevenLabs text-to-speech (needs ELEVENLABS_API_KEY)
  engine "indic-parler-tts"  ai4bharat/indic-parler-tts with a fixed description + seed (needs HF_TOKEN)
Then, per line:
  pitch_semitones   fixed shift from the profile (Bunty +4)
  pitch lock        nudge the line's median pitch to the character's approved sample
                    (cast/<id>/voice/sample.mp3) when it is off by more than 4%, at most 3 semitones
  level             every line normalised to the same loudness, edges trimmed
Lines are cached in work/voicecache/<id>/<hash>.wav (24 kHz mono) so re-renders cost nothing.
build_story.py reads this cache (see LineCache there).
"""
import hashlib, json, os, subprocess, sys, tempfile, urllib.request
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "work", "voicecache")
SR = 24000


def profile(cid):
    return json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))


def cache_path(cid, text, voice):
    key = hashlib.sha1((text + "|" + json.dumps(voice, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:16]
    return os.path.join(CACHE, cid, f"{key}.wav")


def f0_median(x, sr):
    step = max(1, sr // 22050)
    x, sr = x[::step], sr // step
    fr, hop, out = int(0.04 * sr), int(0.01 * sr), []
    for i in range(0, len(x) - fr, hop):
        s = x[i:i + fr]
        if np.sqrt((s ** 2).mean()) < 0.01:
            continue
        s = s - s.mean()
        c = np.correlate(s, s, "full")[fr - 1:]
        lo, hi = int(sr / 500), int(sr / 70)
        k = lo + np.argmax(c[lo:hi])
        if c[k] > 0.3 * c[0]:
            out.append(sr / k)
    return float(np.median(out)) if out else 0.0


def ff(src, dst, af=None, sr=SR):
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(sr)]
    if af:
        cmd += ["-af", af]
    subprocess.run(cmd + [dst], check=True)


def load(path, sr=SR):
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "a.wav")
        ff(path, w, sr=sr)
        a, _ = sf.read(w, dtype="float32")
    return a


def shift(a, semitones):
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, "i.wav"), os.path.join(td, "o.wav")
        sf.write(i, a, SR)
        ff(i, o, af=f"rubberband=pitch={2 ** (semitones / 12):.5f}:formant=preserved")
        b, _ = sf.read(o, dtype="float32")
    return b


class Engines:
    def __init__(self):
        self.parler = None

    def elevenlabs(self, text, v):
        body = json.dumps({"text": text, "model_id": v.get("model_id", "eleven_v3"),
                           "language_code": v.get("language_code", "hi")}).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format=mp3_44100_128", data=body,
            headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"}, method="POST")
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.mp3")
            with urllib.request.urlopen(req, timeout=180) as r:
                open(p, "wb").write(r.read())
            return load(p)

    def indic_parler(self, text, v):
        import torch
        if self.parler is None:
            from parler_tts import ParlerTTSForConditionalGeneration
            from transformers import AutoTokenizer
            tok = os.environ.get("HF_TOKEN")
            torch.set_num_threads(os.cpu_count() or 4)
            m = ParlerTTSForConditionalGeneration.from_pretrained(v["model"], token=tok).eval()
            self.parler = (m, AutoTokenizer.from_pretrained(v["model"], token=tok),
                           AutoTokenizer.from_pretrained(m.config.text_encoder._name_or_path, token=tok))
        m, tok, dtok = self.parler
        torch.manual_seed(v["seed"])
        d = dtok(v["description"], return_tensors="pt")
        p = tok(text, return_tensors="pt")
        with torch.no_grad():
            g = m.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                           prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
        a = g.cpu().numpy().squeeze().astype(np.float32)
        with tempfile.TemporaryDirectory() as td:
            i = os.path.join(td, "i.wav")
            sf.write(i, a, m.config.sampling_rate)
            return load(i)


_targets = {}


def target_pitch(cid):
    if cid not in _targets:
        _targets[cid] = f0_median(load(os.path.join(ROOT, "cast", cid, "voice", "sample.mp3")), SR)
    return _targets[cid]


def render(eng, cid, text):
    v = profile(cid)["voice"]
    out = cache_path(cid, text, v)
    if os.path.exists(out):
        return out, "cached"
    a = eng.elevenlabs(text, v) if v["engine"] == "elevenlabs" else eng.indic_parler(text, v)
    if v.get("pitch_semitones"):
        a = shift(a, v["pitch_semitones"])
    note = ""
    tp, lp = target_pitch(cid), f0_median(a, SR)
    if tp and lp:
        semis = 12 * np.log2(tp / lp)
        if abs(tp / lp - 1) > 0.04:
            semis = float(np.clip(semis, -3, 3))
            a = shift(a, semis)
            note = f"pitch-locked {semis:+.1f} st"
    nz = np.nonzero(np.abs(a) > 0.01)[0]
    if len(nz):
        a = a[max(nz[0] - 600, 0): nz[-1] + 1200]
    rms = np.sqrt(np.mean(a ** 2)) + 1e-9
    a = np.clip(a * (0.08 / rms), -0.98, 0.98)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, a, SR)
    return out, note or "ok"


def main():
    eng = Engines()
    n = 0
    for path in sys.argv[1:]:
        ep = json.load(open(path))
        for sh in ep["shots"]:
            for ln in sh.get("lines", []):
                p, note = render(eng, ln["who"], ln["say"])
                n += 1
                print(f"{os.path.basename(path)}  {ln['who']:8s} {note:22s} {ln.get('caption', ln['say'])[:50]}", flush=True)
    print(f"{n} lines ready in {CACHE}")


if __name__ == "__main__":
    main()
