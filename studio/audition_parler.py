"""Indic Parler-TTS voice audition (free, Apache-2.0, runs on CPU).

    .venv-parler/bin/python studio/audition_parler.py [id ...]

Needs HF_TOKEN with access to ai4bharat/indic-parler-tts (accept the terms on its page).
A voice is a named speaker plus a plain-English description of how they sound.
Writes work/audition/parler/<id>_<n>.wav
"""
import json, os, sys, time
import soundfile as sf
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "ai4bharat/indic-parler-tts"
TAIL = "The recording is very clear, close-sounding, with no background noise."

CASTING = {
    "foxley": ["Rohit speaks in a playful, confident and slightly smug tone with a moderate pitch and a moderate pace, very expressive.",
               "Aman speaks in a warm, clever, theatrical tone with a moderate pitch, expressive, at a moderate pace."],
    "bilal":  ["Aman speaks in an excited, eager, high-pitched voice at a fast pace, very expressive.",
               "Rohit speaks in an eager, slightly high-pitched, enthusiastic voice at a fast pace."],
    "rafiq":  ["Rohit speaks in a loud, deep, dramatic voice with a low pitch at a moderate pace, very expressive.",
               "Aman speaks in a booming, deep, low-pitched and dramatic voice, very expressive."],
    "nusrat": ["Divya speaks in a proud, dramatic and slightly low-pitched voice at a slow pace, very expressive.",
               "Rani speaks in a grand, elegant, slightly low-pitched voice at a slow pace, expressive."],
    "raju":   ["Aman speaks in a friendly, casual and slightly nervous voice with a moderate pitch at a moderate pace.",
               "Rohit speaks in a relaxed, casual, friendly voice with a slightly low pitch."],
    "zara":   ["Divya speaks in a young, sarcastic, high-pitched voice at a fast pace, very expressive.",
               "Rani speaks in a bright, young, confident and high-pitched voice at a fast pace."],
    "ayesha": ["Rani speaks in a calm, precise and measured voice with a moderate pitch at a moderate pace.",
               "Divya speaks in a calm, intelligent, clear voice with a moderate pitch, slightly slow."],
    "jamil":  ["Rohit speaks in a very low-pitched, gruff and grumpy voice of an old man at a slow pace, expressive.",
               "Aman speaks in a deep, raspy, low-pitched old man's voice at a very slow pace, complaining."],
    "faisal": ["Aman speaks in a cheerful, energetic and upbeat voice at a fast pace, very expressive.",
               "Rohit speaks in a happy, friendly, energetic voice with a moderate pitch at a fast pace."],
}


def main():
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    tok = os.environ.get("HF_TOKEN")
    torch.set_num_threads(os.cpu_count() or 4)
    t0 = time.time()
    model = ParlerTTSForConditionalGeneration.from_pretrained(REPO, token=tok).eval()
    tokenizer = AutoTokenizer.from_pretrained(REPO, token=tok)
    desc_tok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path, token=tok)
    sr = model.config.sampling_rate
    print(f"model loaded in {time.time()-t0:.0f}s, sample rate {sr}")
    out_dir = os.path.join(ROOT, "work", "audition", "parler")
    os.makedirs(out_dir, exist_ok=True)
    ids = sys.argv[1:] or list(CASTING)
    for cid in ids:
        line = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))["catchphrase_say"]
        for n, desc in enumerate(CASTING[cid], 1):
            p = os.path.join(out_dir, f"{cid}_{n}.wav")
            if os.path.exists(p):
                continue
            torch.manual_seed(1000 + n)
            d = desc_tok(f"{desc} {TAIL}", return_tensors="pt")
            pr = tokenizer(line, return_tensors="pt")
            t = time.time()
            with torch.no_grad():
                g = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                   prompt_input_ids=pr.input_ids, prompt_attention_mask=pr.attention_mask)
            a = g.cpu().numpy().squeeze()
            sf.write(p, a, sr)
            print(f"{cid:8s} {n}  {len(a)/sr:4.1f}s audio in {time.time()-t:4.0f}s")


if __name__ == "__main__":
    main()
