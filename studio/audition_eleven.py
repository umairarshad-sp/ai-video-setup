"""ElevenLabs voice audition: each character's catchphrase in 2 built-in voices.

    .venv/bin/python studio/audition_eleven.py

Needs ELEVENLABS_API_KEY. On the free plan only ElevenLabs' built-in (premade) voices
work through the API; library voices and voice design need a paid plan.
Writes work/audition/eleven/<id>_<voice>.mp3
"""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = os.environ["ELEVENLABS_API_KEY"]
MODEL = "eleven_v3"

PREMADE = {"Callum": "N2lVS1w4EtoT3dr4eOWO", "Liam": "TX3LPaxmHKxFdv7VOQHJ", "Will": "bIHbv24MWmeRgasZH58o",
           "Brian": "nPczCjzI2devNBz1zQrb", "Adam": "pNInz6obpgDQGcFmaJgB", "Lily": "pFZP5JQG7iQjIQuC4Bku",
           "Alice": "Xb7hH8MSUJpSbSDYk0k2", "Chris": "iP95p4xoKVk53GoZ742B", "Roger": "CwhRBWXzGAHq8TQ4Fs17",
           "Jessica": "cgSgspJ2msm6clMCkdW9", "Laura": "FGY2WhTYpPnrIDTdsKH5", "Matilda": "XrExE9yKIg1WjnnlVkGX",
           "Sarah": "EXAVITQu4vr4xnSDxMaL", "Bill": "pqHfZKP75CvOlQylNhV4", "George": "JBFqnCBsd6RMkjVDRZzb",
           "Eric": "cjVigY5qzO86Huf0OWal", "Charlie": "IKne3meq5aSn9XLyUdCD"}
CASTING = {"foxley": ["Callum", "Charlie"], "bilal": ["Will", "Liam"], "rafiq": ["Brian", "Adam"],
           "nusrat": ["Lily", "Alice"], "raju": ["Chris", "Roger"], "zara": ["Jessica", "Laura"],
           "ayesha": ["Matilda", "Sarah"], "jamil": ["Bill", "George"], "faisal": ["Eric", "Liam"]}


def tts(voice_id, text, out):
    body = json.dumps({"text": text, "model_id": MODEL, "language_code": "hi"}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128", data=body,
        headers={"xi-api-key": KEY, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        open(out, "wb").write(r.read())


def main():
    out_dir = os.path.join(ROOT, "work", "audition", "eleven")
    os.makedirs(out_dir, exist_ok=True)
    chars = 0
    for cid, voices in CASTING.items():
        line = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))["catchphrase_say"]
        for v in voices:
            p = os.path.join(out_dir, f"{cid}_{v}.mp3")
            if not os.path.exists(p):
                tts(PREMADE[v], line, p)
                chars += len(line)
            print(f"{cid:8s} {v:8s} ok")
    print(f"~{chars} credits used")


if __name__ == "__main__":
    main()
