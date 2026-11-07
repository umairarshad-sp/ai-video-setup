"""Character voices: Kokoro TTS + voice blending + pitch shift.

A character's voice recipe lives in cast/<id>/profile.json -> "voice":
    {"base": "hm_omega", "blend": [["am_onyx", 0.3]], "speed": 0.95, "pitch": -2.0}
- base   a Kokoro voice. Hindi voices: hm_omega, hm_psi (male), hf_alpha, hf_beta (female)
- blend  other voices mixed into the base style, with weights (changes the timbre)
- speed  speaking rate
- pitch  semitones, applied after synthesis with ffmpeg rubberband (keeps the length)

Text language: write Hindi/Urdu lines in Devanagari (best pronunciation) and pass lang="hi".
Roman Urdu is read as English, so it is only used for captions.
"""
import os, subprocess, tempfile
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 24000


def detect_lang(text):
    if any("ऀ" <= ch <= "ॿ" for ch in text):
        return "hi"
    if any("؀" <= ch <= "ۿ" for ch in text):
        return "ur"
    return "en-us"


class Voices:
    def __init__(self):
        from kokoro_onnx import Kokoro
        self.tts = Kokoro(os.path.join(ROOT, "models/kokoro-v1.0.onnx"), os.path.join(ROOT, "models/voices-v1.0.bin"))

    def style(self, recipe):
        base = self.tts.get_voice_style(recipe["base"]).astype(np.float32)
        blend = recipe.get("blend") or []
        if not blend:
            return base
        w_base = 1.0 - sum(w for _, w in blend)
        out = base * w_base
        for name, w in blend:
            out = out + self.tts.get_voice_style(name).astype(np.float32) * w
        return out

    def say(self, text, recipe, lang=None):
        if isinstance(recipe, str):
            recipe = {"base": recipe}
        lang = lang or detect_lang(text)
        a, sr = self.tts.create(text, voice=self.style(recipe), speed=recipe.get("speed", 1.0), lang=lang)
        assert sr == SR
        a = a.astype(np.float32)
        if recipe.get("pitch"):
            a = pitch_shift(a, recipe["pitch"])
        # trim silence so cues land on the words
        nz = np.nonzero(np.abs(a) > 0.01)[0]
        if len(nz):
            a = a[max(nz[0] - 600, 0): nz[-1] + 1200]
        return a


def pitch_shift(a, semitones):
    ratio = 2 ** (semitones / 12)
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, "i.wav"), os.path.join(td, "o.wav")
        sf.write(i, a, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", i, "-af", f"rubberband=pitch={ratio:.5f}", o], check=True)
        b, _ = sf.read(o, dtype="float32")
    return b


def recipe_for(cid):
    import json
    return json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))["voice"]


if __name__ == "__main__":
    # audition: every character says their catchphrase; writes work/voices/<id>.wav and all.wav
    import json
    v = Voices()
    os.makedirs(os.path.join(ROOT, "work", "voices"), exist_ok=True)
    order = ["foxley", "bilal", "rafiq", "nusrat", "raju", "zara", "ayesha", "jamil", "faisal"]
    parts = []
    for cid in order:
        prof = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))
        a = v.say(prof["catchphrase_say"], prof["voice"])
        sf.write(os.path.join(ROOT, "work", "voices", f"{cid}.wav"), a, SR)
        parts += [a, np.zeros(int(0.8 * SR), np.float32)]
        print(f"{prof['name']:18s} {len(a)/SR:4.1f}s  {prof['catchphrase']}")
    sf.write(os.path.join(ROOT, "work", "voices", "all.wav"), np.concatenate(parts), SR)
