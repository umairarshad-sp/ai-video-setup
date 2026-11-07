"""Join audition clips into one labelled track: a short spoken label, then the clip.

    .venv/bin/python studio/audition_pack.py eleven    # work/audition/eleven/*.mp3 -> audition_eleven.m4a
    .venv/bin/python studio/audition_pack.py parler    # work/audition/parler/*.wav -> audition_parler.m4a
"""
import glob, os, subprocess, sys, tempfile
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "studio"))
SR = 24000
ORDER = ["foxley", "bilal", "rafiq", "nusrat", "raju", "zara", "ayesha", "jamil", "faisal"]
NAMES = {"foxley": "Foxley", "bilal": "Constable Bilal", "rafiq": "Ustad Rafiq", "nusrat": "Begum Nusrat",
         "raju": "Raju Mistri", "zara": "Zara", "ayesha": "Doctor Ayesha", "jamil": "Chacha Jamil", "faisal": "Faisal"}


def load(path):
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ac", "1", "-ar", str(SR), w], check=True)
        a, _ = sf.read(w, dtype="float32")
    return a / (np.max(np.abs(a)) + 1e-9) * 0.8


def main():
    src = sys.argv[1]
    from voices import Voices
    v = Voices()
    files = sorted(glob.glob(os.path.join(ROOT, "work", "audition", src, "*.*")))
    parts = []
    for cid in ORDER:
        mine = [f for f in files if os.path.basename(f).startswith(cid + "_")]
        for k, f in enumerate(mine):
            label = v.say(f"{NAMES[cid]}, option {'ABC'[k]}.", {"base": "af_heart", "speed": 1.1}, lang="en-us")
            parts += [label * 0.6, np.zeros(int(0.35 * SR), np.float32), load(f), np.zeros(int(0.9 * SR), np.float32)]
    out = os.path.join(ROOT, "work", "audition", f"audition_{src}.wav")
    sf.write(out, np.concatenate(parts), SR)
    m4a = out[:-4] + ".m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-c:a", "aac", "-b:a", "128k", m4a], check=True)
    print("wrote", m4a)


if __name__ == "__main__":
    main()
