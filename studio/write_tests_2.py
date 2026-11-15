"""Writes the second round of test formats (2026-11-15):

  episodes/wit_001.json    "17 Oont"      Akbar-Birbal style wit story (format 1), camels drawn in code
  episodes/doors_001.json  "Teen Darwaze" choice riddle (format 3), doors, fire, snakes and lion drawn in code

    python3 studio/write_tests_2.py
Both are single self-contained Reels (answer included, last shot = first shot so they loop).
Uses the "overlay" shot key of build_story.py (raw SVG/HTML + GSAP lines with @L/@E time tokens).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2B2B2B"


def ln(who, cap, say, en, **k):
    return {"who": who, "caption": cap, "say": say, "en": en, **k}


# ------------------------------------------------------------------ camels
def camel_svg(fill="#E3B467", extra=False):
    blanket = '<path d="M44 33 h34 v14 h-34z" fill="#C8342B" stroke="#2B2B2B" stroke-width="3"/>' if extra else ""
    return (f'<svg viewBox="0 0 124 100" width="100%" height="100%">'
            f'<g stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M34 62 v30 M46 64 v28 M80 64 v28 M92 62 v30" fill="none" stroke-width="7"/>'
            f'<path d="M18 52 q-8 6 -6 16" fill="none"/>'
            f'<ellipse cx="60" cy="56" rx="42" ry="17" fill="{fill}"/>'
            f'<path d="M36 46 q16 -40 34 -2 q6 -14 16 4" fill="{fill}"/>'
            f'<path d="M96 54 q16 -14 10 -34" fill="none" stroke-width="15"/>'
            f'<path d="M96 54 q16 -14 10 -34" fill="none" stroke="{fill}" stroke-width="8"/>'
            f'<ellipse cx="109" cy="18" rx="12" ry="8" fill="{fill}"/>'
            f'<circle cx="112" cy="16" r="2" fill="{INK}" stroke="none"/></g>{blanket}</svg>')


PANEL_Y = 640
GRID = [(90 + (i % 6) * 155, PANEL_Y + 34 + (i // 6) * 105) for i in range(18)]
SPLIT = ([(80 + (i % 3) * 110, PANEL_Y + 78 + (i // 3) * 92) for i in range(9)] +          # Raju 9
         [(450 + (i % 2) * 110, PANEL_Y + 78 + (i // 2) * 92) for i in range(6)] +         # Faisal 6
         [(700, PANEL_Y + 78 + i * 92) for i in range(2)] +                                  # Zara 2
         [(885, PANEL_Y + 170)])                                                             # the extra camel
LABELS = [("RAJU · 9", 70, 330), ("FAISAL · 6", 440, 230), ("ZARA · 2", 690, 140), ("BACHA · 1", 850, 170)]


def camels_overlay(n=17, extra=False, start_split=False, extra_at=None, split_at=None, home_at=None):
    """n camels in a grid; optionally a red-blanket 18th (Jamil's) pops in, then all split 9/6/2 + 1"""
    items, js, sfx = [], [], []
    count = 18 if extra else n
    for i in range(count):
        x, y = SPLIT[i] if start_split else GRID[i]
        sc = 0.85 if start_split else 1.0
        is_x = extra and i == 17
        items.append(f'<div id="{{sid}}-c{i}" style="position:absolute;left:{x}px;top:{y}px;width:124px;height:100px;'
                     f'transform-origin:0 0;transform:scale({sc})">{camel_svg("#F2B134" if is_x else "#E3B467", is_x)}</div>')
    if extra and extra_at:
        js.append(f'tl.fromTo("#{{sid}}-c17", {{opacity: 0, y: -160, scale: 0.4}}, {{opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "bounce.out"}}, {extra_at});')
        sfx.append(["pop", extra_at])
    if split_at:
        for i in range(count):
            (gx, gy), (sx, sy) = GRID[i], SPLIT[i]
            js.append(f'tl.to("#{{sid}}-c{i}", {{x: {sx - gx}, y: {sy - gy}, scale: 0.85, duration: 0.6, ease: "power2.inOut"}}, {split_at}+{0.02 * i:.2f});')
        sfx.append(["whoosh", split_at])
    labels = ""
    if split_at or start_split:
        for k, (t, x, w) in enumerate(LABELS):
            labels += (f'<div id="{{sid}}-lb{k}" style="position:absolute;left:{x}px;top:{PANEL_Y + 14}px;width:{w}px;text-align:center;'
                       f'font-weight:900;font-size:34px;color:#fff;background:{"#C8342B" if k == 3 else "#1F4E5F"};border:5px solid {INK};border-radius:16px;'
                       f'opacity:{1 if start_split else 0}">{t}</div>')
            if split_at:
                js.append(f'tl.fromTo("#{{sid}}-lb{k}", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {split_at}+{0.7 + 0.35 * k:.2f});')
                sfx.append(["pop", f"{split_at}+{0.7 + 0.35 * k:.2f}"])
    if home_at:   # the extra camel bounces: "and my camel comes back to me"
        js.append(f'tl.to("#{{sid}}-c17", {{y: "-=40", duration: 0.25, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {home_at});')
    panel = (f'<div style="position:absolute;left:40px;right:40px;top:{PANEL_Y}px;height:{350 if (split_at or start_split) else 340}px;'
             f'background:rgba(255,248,230,0.92);border:8px solid {INK};border-radius:30px;box-shadow:0 12px 0 {INK}"></div>')
    counter = ""
    if not (split_at or start_split):
        counter = (f'<div style="position:absolute;right:60px;top:{PANEL_Y - 40}px;background:#C8342B;color:#fff;font-weight:900;font-size:44px;'
                   f'padding:4px 22px;border:6px solid {INK};border-radius:22px">{"18" if extra else "17"} OONT</div>')
        if extra and extra_at:
            counter = (f'<div id="{{sid}}-cnt" style="position:absolute;right:60px;top:{PANEL_Y - 40}px;background:#C8342B;color:#fff;font-weight:900;font-size:44px;'
                       f'padding:4px 22px;border:6px solid {INK};border-radius:22px">17 + 1 = 18</div>')
            js.append(f'tl.fromTo("#{{sid}}-cnt", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {extra_at}+0.4);')
    return {"html": panel + counter + "".join(items) + labels, "js": js, "sfx": sfx}


TRIO = [{"id": "raju", "x": 0.2}, {"id": "faisal", "x": 0.5}, {"id": "zara", "x": 0.8}]
CAM = {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}}
RULES = {"title": "SHART", "rows": [["RAJU", "AADHE (1/2)"], ["FAISAL", "TEESRA HISSA (1/3)"], ["ZARA", "NAUVAN HISSA (1/9)"]], "y": 1060, "rot": -3}

wit = {"number": 201, "part": 1, "slug": "wit_001", "format": "1: wit story (Akbar-Birbal style), answer included, loops",
       "title": {"ur": "17 OONT", "en": "17 CAMELS"}, "handle": "@AskFoxley", "music": {"bpm": 100, "gain": 0.5},
       "answer_note": "Jamil lends one camel: 18 -> 9 + 6 + 2 = 17, and his own camel is left over.",
       "shots": [
    {"set": "gali_street", "cast": TRIO, "camera": CAM, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1,
     "hook": {"text": "17 OONT, 3 DOST... AUR EK MUSHKIL!", "y": 110, "dur": 99},
     "overlay": camels_overlay(17),
     "lines": [ln("foxley", "Teen doston ne inaam mein satrah oont jeete.", "तीन दोस्तों ने इनाम में सत्रह ऊँट जीते।",
                  "Three friends won seventeen camels as a prize.")]},
    {"set": "gali_street", "transition": "whoosh", "cast": TRIO, "camera": CAM, "caption_y": 230, "hold": 0.5,
     "card": {**RULES, "at": -1},
     "lines": [ln("foxley", "Shart yeh thi: Raju ko aadhe, Faisal ko teesra hissa, aur Zara ko nauvan hissa.",
                  "शर्त ये थी: राजू को आधे, फ़ैसल को तीसरा हिस्सा, और ज़ारा को नौवाँ हिस्सा।",
                  "The rule: Raju gets half, Faisal a third, and Zara a ninth.")]},
    {"set": "gali_street", "transition": "whoosh", "cast": [{"id": "raju", "x": 0.5}],
     "camera": {"from": {"focus": "raju", "zoom": 1.25}, "to": {"focus": "raju", "zoom": 1.4}}, "hold": 0.3,
     "lines": [ln("raju", "Satrah ka aadha? Saadhe aath oont? Ek oont ko kaatein kya?!",
                  "सत्रह का आधा? साढ़े आठ ऊँट? एक ऊँट को काटें क्या?!",
                  "Half of seventeen? Eight and a half camels? Do we cut a camel in half?!", after="shocked")]},
    {"set": "gali_street", "transition": "whoosh", "cast": TRIO, "camera": CAM, "caption_y": 1290,
     "overlay": camels_overlay(17), "timer": 3, "timer_y": 1500, "sfx": [["riser", 0.0]],
     "cta": {"after_timer": True, "y": 160, "main": "TUM KYA KARTE? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."}, "hold": 0.6,
     "lines": [ln("foxley", "Kisi oont ko kaate bina, kaise baantoge? Socho!", "किसी ऊँट को काटे बिना, कैसे बाँटोगे? सोचो!",
                  "How would you share them without cutting a camel? Think!")]},
    {"set": "gali_street", "transition": "whoosh", "cast": [{"id": "jamil", "x": 0.5}], "caption_y": 230, "hold": 0.4,
     "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}},
     "overlay": camels_overlay(17, extra=True, extra_at="@L0+1.2", split_at="@L1+0.6"),
     "lines": [ln("jamil", "Lo beta, mera ek oont bhi le lo!", "लो बेटा, मेरा एक ऊँट भी ले लो!", "Here, take one of my camels too!"),
               ln("foxley", "Ab atharah! Aadhe nau, teesra hissa chhe, aur nauvan hissa do.",
                  "अब अठारह! आधे नौ, तीसरा हिस्सा छह, और नौवाँ हिस्सा दो।",
                  "Now eighteen! Half is nine, a third is six, and a ninth is two.", sfx_before="reveal")]},
    {"set": "gali_street", "cast": [{"id": "jamil", "x": 0.5}], "caption_y": 230, "hold": 0.6,
     "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.04}, "to": {"focus": [0.5, 0.62], "zoom": 1.1}},
     "overlay": camels_overlay(17, extra=True, start_split=True, home_at="@L1+0.3"),
     "stamp": {"text": "KAMAAL!", "on": "jamil", "line": 1, "y": 1520},
     "lines": [ln("foxley", "Nau, chhe aur do... kul satrah! Ek oont bach gaya.", "नौ, छह और दो... कुल सत्रह! एक ऊँट बच गया।",
                  "Nine, six and two... seventeen in all! One camel is left over."),
               ln("jamil", "Aur mera oont, wapas mere paas!", "और मेरा ऊँट, वापस मेरे पास!", "And my camel comes right back to me!",
                  after="signature_cane_shake")]},
    {"set": "gali_street", "cast": TRIO, "camera": CAM, "overlay": camels_overlay(17), "hold": 0.6},
]}


# ------------------------------------------------------------------ doors
FIRE = ('<svg viewBox="0 0 200 200" width="100%" height="100%"><g stroke="#2B2B2B" stroke-width="5" stroke-linejoin="round">'
        '<path d="M100 188 C40 188 30 130 62 92 C60 118 78 124 82 112 C70 76 96 46 112 18 C116 58 150 70 150 118 C162 108 164 92 160 80 C190 120 176 188 100 188Z" fill="#E8432B"/>'
        '<path d="M100 186 C66 186 62 148 84 126 C86 142 98 144 100 132 C98 112 110 96 118 84 C124 110 144 126 138 154 C134 176 120 186 100 186Z" fill="#F2B134"/>'
        '<path d="M100 184 C84 184 82 166 94 154 C98 164 106 160 106 150 C116 160 120 184 100 184Z" fill="#FFF1A8"/></g></svg>')
SNAKES = ('<svg viewBox="0 0 200 200" width="100%" height="100%"><g stroke="#2B2B2B" stroke-width="5" stroke-linecap="round" fill="none">'
          '<path d="M30 170 C60 140 20 120 50 95 C80 70 40 50 70 32" stroke="#2B2B2B" stroke-width="22"/>'
          '<path d="M30 170 C60 140 20 120 50 95 C80 70 40 50 70 32" stroke="#4CAF50" stroke-width="13"/>'
          '<path d="M130 175 C160 150 120 130 150 105 C180 82 140 62 165 42" stroke="#2B2B2B" stroke-width="22"/>'
          '<path d="M130 175 C160 150 120 130 150 105 C180 82 140 62 165 42" stroke="#8BC34A" stroke-width="13"/></g>'
          '<g stroke="#2B2B2B" stroke-width="4"><ellipse cx="74" cy="28" rx="17" ry="12" fill="#4CAF50"/><ellipse cx="169" cy="38" rx="17" ry="12" fill="#8BC34A"/></g>'
          '<circle cx="79" cy="24" r="3" fill="#2B2B2B"/><circle cx="174" cy="34" r="3" fill="#2B2B2B"/>'
          '<path d="M90 30 l12 2 m-6 -1 l5 -4 m-5 4 l5 4" stroke="#C8342B" stroke-width="3"/><path d="M185 40 l12 2 m-6 -1 l5 -4 m-5 4 l5 4" stroke="#C8342B" stroke-width="3"/></svg>')


def lion(dead=False):
    eyes = ('<path d="M76 92 l16 16 m0 -16 l-16 16 M110 92 l16 16 m0 -16 l-16 16" stroke="#2B2B2B" stroke-width="6" stroke-linecap="round"/>' if dead else
            '<circle cx="84" cy="98" r="8" fill="#2B2B2B"/><circle cx="118" cy="98" r="8" fill="#2B2B2B"/><circle cx="87" cy="95" r="3" fill="#fff"/><circle cx="121" cy="95" r="3" fill="#fff"/>')
    mouth = ('<path d="M86 140 q15 -10 30 0" fill="none" stroke="#2B2B2B" stroke-width="5" stroke-linecap="round"/><path d="M98 138 v14" stroke="#2B2B2B" stroke-width="4"/>' if dead else
             '<path d="M84 132 q17 22 34 0" fill="#C8342B" stroke="#2B2B2B" stroke-width="5"/><path d="M90 133 l4 8 l4 -8 M106 133 l4 8 l4 -8" fill="#fff" stroke="#2B2B2B" stroke-width="2"/>')
    mane = "".join(f'<circle cx="{100 + 70 * __import__("math").cos(a / 12 * 6.283):.1f}" cy="{106 + 70 * __import__("math").sin(a / 12 * 6.283):.1f}" r="26" fill="#B5651D" stroke="#2B2B2B" stroke-width="5"/>' for a in range(12))
    halo = '<ellipse cx="100" cy="22" rx="40" ry="10" fill="none" stroke="#F2B134" stroke-width="7"/>' if dead else ""
    return (f'<svg viewBox="0 0 200 200" width="100%" height="100%">{halo}{mane}'
            '<circle cx="100" cy="106" r="62" fill="#F2B134" stroke="#2B2B2B" stroke-width="5"/>'
            '<circle cx="62" cy="58" r="14" fill="#F2B134" stroke="#2B2B2B" stroke-width="5"/><circle cx="138" cy="58" r="14" fill="#F2B134" stroke="#2B2B2B" stroke-width="5"/>'
            f'{eyes}<path d="M92 116 h18 l-9 10z" fill="#5A2E14" stroke="#2B2B2B" stroke-width="4" stroke-linejoin="round"/>{mouth}</svg>')


DOOR_X = [40, 375, 710]
DOOR_Y = 600
LABELS_D = ["AAG", "ZEHREELE SAANP", "SHER: 3 SAAL SE BHOOKA"]


def doors_overlay(pulse=None, answer=None):
    """three rooms side by side; pulse = [(door, time)], answer = time when 1 and 2 get a red X and the lion is dead"""
    html, js, sfx = "", [], []
    for k, x in enumerate(DOOR_X):
        icon = [FIRE, SNAKES, lion()][k]
        html += (f'<div id="{{sid}}-d{k}" style="position:absolute;left:{x}px;top:{DOOR_Y}px;width:330px;transform-origin:50% 50%">'
                 f'<div style="margin:0 10px;height:420px;background:#6B3F22;border:9px solid {INK};border-radius:24px 24px 8px 8px;box-shadow:0 12px 0 {INK};position:relative">'
                 f'<div style="position:absolute;left:18px;right:18px;top:60px;height:300px;background:#FFF5DC;border:6px solid {INK};border-radius:16px;overflow:hidden">'
                 f'<div style="position:absolute;left:10px;right:10px;top:10px;bottom:10px">{icon}</div>'
                 + (f'<div id="{{sid}}-dead" style="position:absolute;left:10px;right:10px;top:10px;bottom:10px;opacity:0;background:#FFF5DC">{lion(True)}</div>' if k == 2 else "")
                 + f'</div>'
                 f'<div style="position:absolute;left:50%;top:-34px;margin-left:-44px;width:88px;height:88px;border-radius:50%;background:#F2B134;border:8px solid {INK};'
                 f'display:flex;align-items:center;justify-content:center;font-weight:900;font-size:56px;color:{INK}">{k + 1}</div></div>'
                 f'<div style="margin:22px 6px 0;text-align:center;background:#fff;border:6px solid {INK};border-radius:16px;font-weight:900;font-size:{36 if k < 2 else 30}px;'
                 f'line-height:1.1;padding:8px 6px;color:{INK}">{LABELS_D[k]}</div>'
                 f'<div id="{{sid}}-x{k}" style="position:absolute;left:30px;right:30px;top:40px;height:380px;opacity:0">'
                 f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%"><path d="M12 12 L88 88 M88 12 L12 88" stroke="#C8342B" stroke-width="12" stroke-linecap="round"/></svg></div></div>')
    for k, t in (pulse or []):
        js.append(f'tl.fromTo("#{{sid}}-d{k}", {{scale: 1}}, {{scale: 1.12, duration: 0.25, yoyo: true, repeat: 1, ease: "sine.inOut"}}, {t});')
        sfx.append(["pop", t])
    if answer:
        for k in (0, 1):
            js.append(f'tl.fromTo("#{{sid}}-x{k}", {{opacity: 0, scale: 1.6}}, {{opacity: 0.9, scale: 1, duration: 0.25, ease: "back.out(2)"}}, {answer}+{0.3 * k:.1f});')
            sfx.append(["stamp", f"{answer}+{0.3 * k:.1f}"])
        js.append(f'tl.to("#{{sid}}-d2", {{scale: 1.15, duration: 0.4, ease: "back.out(2)"}}, {answer}+0.8);')
        js.append(f'tl.to("#{{sid}}-dead", {{opacity: 1, duration: 0.3}}, {answer}+1.4);')
        sfx.append(["reveal", f"{answer}+0.8"])
    return {"html": html, "js": js, "sfx": sfx}


BUNTY = [{"id": "bunty", "x": 0.5}]
CAMD = {"from": {"focus": [0.5, 0.6], "zoom": 1.0}, "to": {"focus": [0.5, 0.6], "zoom": 1.03}}
doors = {"number": 202, "part": 1, "slug": "doors_001", "format": "3: choice riddle, answer included, loops",
         "title": {"ur": "TEEN DARWAZE", "en": "THREE DOORS"}, "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5},
         "answer_note": "Door 3: a lion that hasn't eaten for 3 years is long dead.",
         "shots": [
    {"set": "police_station", "dark": 0.35, "cast": BUNTY, "camera": CAMD, "sfx": [["sting", 0.0]], "caption_y": 1300, "hold": 0.1,
     "hook": {"text": "90% LOG GALAT DARWAZA CHUNTE HAIN!", "y": 110, "dur": 99}, "overlay": doors_overlay(),
     "lines": [ln("foxley", "Tum qaid mein ho. Bahar nikalne ke sirf teen raaste hain.", "तुम क़ैद में हो। बाहर निकलने के सिर्फ़ तीन रास्ते हैं।",
                  "You're locked up. There are only three ways out.")]},
    {"set": "police_station", "dark": 0.35, "cast": BUNTY, "camera": CAMD, "caption_y": 1300, "hold": 0.2,
     "overlay": doors_overlay(pulse=[(0, "@L0+0.2"), (1, "@L1+0.2"), (2, "@L2+0.2")]),
     "lines": [ln("foxley", "Pehle kamre mein bhadakti aag.", "पहले कमरे में भड़कती आग।", "Room one: a blazing fire."),
               ln("foxley", "Doosre mein zehreele saanp.", "दूसरे में ज़हरीले साँप।", "Room two: poisonous snakes."),
               ln("foxley", "Teesre mein ek sher, jis ne teen saal se kuch nahi khaya.", "तीसरे में एक शेर, जिसने तीन साल से कुछ नहीं खाया।",
                  "Room three: a lion that hasn't eaten in three years.")]},
    {"set": "police_station", "dark": 0.35, "transition": "whoosh", "cast": [{"id": "bunty", "x": 0.5}],
     "camera": {"from": {"focus": "bunty", "zoom": 1.3}, "to": {"focus": "bunty", "zoom": 1.45}}, "hold": 0.2,
     "lines": [ln("bunty", "Baap re! Main kaunsa darwaza kholoon?", "बाप रे! मैं कौनसा दरवाज़ा खोलूँ?", "Oh no! Which door do I open?", after="nervous")]},
    {"set": "police_station", "dark": 0.35, "transition": "whoosh", "cast": BUNTY, "camera": CAMD, "caption_y": 1300,
     "overlay": doors_overlay(), "timer": 3, "timer_y": 1500, "sfx": [["riser", 0.0]],
     "cta": {"after_timer": True, "y": 160, "main": "1, 2 YA 3? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."}, "hold": 0.6,
     "lines": [ln("foxley", "Tum kaunsa chunoge? Teen second!", "तुम कौनसा चुनोगे? तीन सेकंड!", "Which one would you pick? Three seconds!")]},
    {"set": "police_station", "dark": 0.35, "transition": "whoosh", "cast": BUNTY, "camera": CAMD, "caption_y": 1300, "hold": 0.5,
     "overlay": doors_overlay(answer="@L0+0.1"),
     "stamp": {"text": "BACH GAYE!", "on": "bunty", "line": 2, "y": 130},
     "lines": [ln("foxley", "Teesra darwaza!", "तीसरा दरवाज़ा!", "Door number three!"),
               ln("foxley", "Jo sher teen saal se bhooka ho... woh kab ka mar chuka hoga!", "जो शेर तीन साल से भूखा हो... वो कब का मर चुका होगा!",
                  "A lion that hasn't eaten in three years... died long ago!"),
               ln("bunty", "Waah! Main bach gaya!", "वाह! मैं बच गया!", "Yay! I'm saved!")]},
    {"set": "police_station", "dark": 0.35, "cast": BUNTY, "camera": CAMD, "overlay": doors_overlay(), "hold": 0.6},
]}

for name, ep in (("wit_001", wit), ("doors_001", doors)):
    json.dump(ep, open(os.path.join(ROOT, "episodes", f"{name}.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote episodes/%s.json" % name)
