"""Writes riddles 6-9 of planning/NEW_RIDDLES.md (2026-11-23), props drawn in code:

  episodes/riddle_nadi.json       Nadi Paar                     river crossing   set: river_ghat    (stand-in: town_park)
  episodes/riddle_matke.json      Do Matke                      water pouring    set: desert_village (stand-in: kitchen)
  episodes/riddle_pehredaar.json  Sach aur Jhooth ke Pehredaar  liar/truth gate  set: qila_gate     (stand-in: police_station)
  episodes/riddle_balti.json      Kaunsi Balti Pehle Bharegi?   pipes            set: chhat_rooftop (stand-in: gali_street)

    python3 studio/write_riddles_4.py
When the owner's backgrounds exist in sets/<id>/background.png, the real set is used automatically.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2B2B2B"
PY = 600


def set_or(real, stand_in):
    return real if os.path.exists(os.path.join(ROOT, "sets", real, "background.png")) else stand_in


def ln(who, cap, say, en, **k):
    return {"who": who, "caption": cap, "say": say, "en": en, **k}


def ov(html, js=(), sfx=()):
    return {"html": html, "js": list(js), "sfx": [list(s) for s in sfx]}


def panel(top, h, bg="rgba(255,248,230,0.94)", title=None):
    t = (f'<div style="position:absolute;left:0;right:0;top:-34px;text-align:center"><span style="background:#1F4E5F;color:#fff;font-weight:900;'
         f'font-size:36px;padding:4px 24px;border:6px solid {INK};border-radius:18px">{title}</span></div>') if title else ""
    return (f'<div style="position:absolute;left:40px;right:40px;top:{top}px;height:{h}px;background:{bg};border:8px solid {INK};'
            f'border-radius:30px;box-shadow:0 12px 0 {INK};overflow:visible">{t}</div>')


def badge(n, x, y, size=60, fs=38):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;border-radius:50%;background:#F2B134;'
            f'border:6px solid {INK};display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{fs}px;color:{INK};z-index:3">{n}</div>')


def tag(text, x, y, idx, bg="#C8342B", fs=36):
    return (f'<div id="{{sid}}-{idx}" style="position:absolute;left:{x}px;top:{y}px;background:{bg};color:#fff;font-weight:900;font-size:{fs}px;'
            f'white-space:nowrap;padding:4px 18px;border:5px solid {INK};border-radius:16px;opacity:0;z-index:4">{text}</div>')


def pop(idx, t):
    return f'tl.fromTo("#{{sid}}-{idx}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t});'


def cam(z0=1.0, z1=1.03):
    return {"from": {"focus": [0.5, 0.62], "zoom": z0}, "to": {"focus": [0.5, 0.62], "zoom": z1}}


def question_shot(set_, cast, overlay, text, say, en, main="1, 2 YA 3? COMMENT KARO!", timer=3, **k):
    return {"set": set_, "transition": "whoosh", "cast": cast, "camera": cam(), "feet": 0.93, "overlay": overlay,
            "timer": timer, "timer_y": 1500, "caption_y": 1290, "sfx": [["riser", 0.0]], "hold": 0.6,
            "cta": {"after_timer": True, "y": 160, "main": main, "sub": "Jawab abhi aa raha hai..."},
            "lines": [ln("foxley", text, say, en)], **k}


EPS = {}

# ===================================================================== 6. Nadi Paar
def svg_goat():
    return (f'<svg viewBox="0 0 120 96" width="100%" height="100%"><g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M34 66 v24 M46 68 v22 M76 68 v22 M88 66 v24" stroke-width="6"/>'
            f'<ellipse cx="60" cy="56" rx="36" ry="20" fill="#FFFFFF"/><path d="M26 52 q-8 -2 -10 8" fill="none"/>'
            f'<ellipse cx="96" cy="36" rx="16" ry="13" fill="#FFFFFF"/><path d="M88 24 q-4 -14 8 -18 M100 24 q4 -14 14 -12" fill="none" stroke="#8A5A2B" stroke-width="5"/>'
            f'<path d="M100 48 q2 10 -4 14" fill="none"/></g><circle cx="100" cy="33" r="2.5" fill="{INK}"/></svg>')


def svg_wolf():
    return (f'<svg viewBox="0 0 120 96" width="100%" height="100%"><g stroke="{INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M34 66 v24 M46 68 v22 M76 68 v22 M88 66 v24" stroke-width="6"/>'
            f'<path d="M22 58 q-16 -10 -16 -26 q10 8 20 16" fill="#8E8E8E"/>'
            f'<ellipse cx="60" cy="56" rx="36" ry="19" fill="#8E8E8E"/>'
            f'<path d="M84 30 l6 -20 l8 14 l8 -14 l4 20 q12 6 12 16 q-12 6 -24 4 q-14 -2 -14 -20z" fill="#8E8E8E"/></g>'
            f'<circle cx="100" cy="32" r="3" fill="#F2B134"/><circle cx="118" cy="46" r="3" fill="{INK}"/></svg>')


def svg_grass():
    return (f'<svg viewBox="0 0 120 96" width="100%" height="100%"><g stroke="{INK}" stroke-width="4" stroke-linejoin="round">'
            f'<path d="M30 90 q-6 -50 -22 -70 q20 10 34 40 q2 -40 18 -56 q-4 30 2 56 q10 -40 34 -50 q-18 26 -16 60 q12 -20 30 -24 q-16 18 -20 44z" fill="#7CB342"/>'
            f'<rect x="38" y="62" width="44" height="12" rx="4" fill="#C98A1C"/></g></svg>')


def svg_boat():
    return (f'<svg viewBox="0 0 200 70" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
            f'<path d="M6 16 h188 q-14 46 -60 48 h-68 q-46 -2 -60 -48z" fill="#8A5A2B"/><path d="M20 30 h160" stroke="#5A3A1E" stroke-width="4"/></g></svg>')


L_X, R_X = 70, 880                    # bank slot x
ROWS = [PY + 40, PY + 160, PY + 280]  # wolf, goat, grass
DOCK_L, DOCK_R = 260, 620             # boat x
BOAT_Y = PY + 300
ON_BOAT_Y = PY + 218
ITEM = {"wolf": 0, "goat": 1, "grass": 2}


def river(trips=(), numbers=False):
    """trips: list of (time expr, item or None, side to go to 'R'/'L')"""
    html = panel(PY - 10, 430, bg="#6EC6F0", title="NADI PAAR")
    html += (f'<div style="position:absolute;left:48px;top:{PY - 2}px;width:200px;height:414px;background:#C9A36A;border-radius:22px 0 0 22px"></div>'
             f'<div style="position:absolute;left:832px;top:{PY - 2}px;width:200px;height:414px;background:#C9A36A;border-radius:0 22px 22px 0"></div>')
    for k in range(6):
        html += (f'<div style="position:absolute;left:{300 + (k % 3) * 160}px;top:{PY + 40 + (k // 3) * 150}px;width:90px;height:18px;'
                 f'border-top:5px solid rgba(255,255,255,0.7);border-radius:50%"></div>')
    html += f'<div id="{{sid}}-boat" style="position:absolute;left:{DOCK_L}px;top:{BOAT_Y}px;width:200px;height:70px;z-index:2">{svg_boat()}</div>'
    for name, svg in (("wolf", svg_wolf()), ("goat", svg_goat()), ("grass", svg_grass())):
        r = ITEM[name]
        html += f'<div id="{{sid}}-{name}" style="position:absolute;left:{L_X}px;top:{ROWS[r]}px;width:120px;height:96px;z-index:3">{svg}</div>'
        if numbers:
            html += badge({"wolf": 1, "goat": 2, "grass": 3}[name], L_X + 120, ROWS[r] + 10)
    js, sfx = [], []
    pos = {n: ("L", 0, 0) for n in ITEM}   # side, current dx, dy
    boat_dx = 0
    for t, item, side in trips:
        target_boat = DOCK_R - DOCK_L if side == "R" else 0
        if item is None:
            js.append(f'tl.to("#{{sid}}-boat", {{x: {target_boat}, duration: 0.8, ease: "sine.inOut"}}, {t});')
            sfx.append(["whoosh", t])
            boat_dx = target_boat
            continue
        r = ITEM[item]
        on_boat_dx_start = DOCK_L + boat_dx + 40 - L_X
        on_boat_dx_end = DOCK_L + target_boat + 40 - L_X
        dy_boat = ON_BOAT_Y - ROWS[r]
        dest_dx = (R_X - L_X) if side == "R" else 0
        js += [f'tl.to("#{{sid}}-{item}", {{x: {on_boat_dx_start}, y: {dy_boat}, duration: 0.3, ease: "power2.out"}}, {t});',
               f'tl.to("#{{sid}}-boat", {{x: {target_boat}, duration: 0.8, ease: "sine.inOut"}}, {t}+0.35);',
               f'tl.to("#{{sid}}-{item}", {{x: {on_boat_dx_end}, duration: 0.8, ease: "sine.inOut"}}, {t}+0.35);',
               f'tl.to("#{{sid}}-{item}", {{x: {dest_dx}, y: 0, duration: 0.3, ease: "back.out(2)"}}, {t}+1.2);']
        sfx += [["whoosh", f"{t}+0.35"], ["pop", f"{t}+1.3"]]
        boat_dx = target_boat
    return ov(html, js, sfx)


RULES_NADI = {"title": "MUSHKIL", "rows": [["BHEDIYA + BAKRI", "BAKRI GAYI!"], ["BAKRI + GHAAS", "GHAAS GAYI!"], ["KASHTI MEIN", "RAJU + 1 CHEEZ"]],
              "y": 640, "rot": -2, "at": -1}
SET6 = set_or("river_ghat", "town_park")
RAJU = [{"id": "raju", "x": 0.5}]
EPS["riddle_nadi"] = {"number": 306, "part": 1, "slug": "riddle_nadi", "title": {"ur": "NADI PAAR", "en": "THE RIVER CROSSING"},
  "handle": "@AskFoxley", "music": {"bpm": 100, "gain": 0.5},
  "answer_note": "Goat over; back; wolf over; goat back; grass over; back; goat over.",
  "shots": [
    {"set": SET6, "cast": RAJU, "camera": cam(), "feet": 0.93, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1,
     "hook": {"text": "SIRF EK KASHTI... AUR TEEN MUSIBATEIN!", "y": 110, "dur": 99}, "overlay": river(),
     "lines": [ln("foxley", "Raju ko bhediya, bakri aur ghaas nadi paar le jaani hai.", "राजू को भेड़िया, बकरी और घास नदी पार ले जानी है।",
                  "Raju has to take a wolf, a goat and some grass across the river.")]},
    {"set": SET6, "transition": "whoosh", "cast": RAJU, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.3, "card": RULES_NADI,
     "lines": [ln("foxley", "Kashti mein sirf ek cheez! Aur akele chhodo to bhediya bakri kha jayega, bakri ghaas.",
                  "कश्ती में सिर्फ़ एक चीज़! और अकेले छोड़ो तो भेड़िया बकरी खा जाएगा, बकरी घास।",
                  "Only one thing fits in the boat! Left alone, the wolf eats the goat, and the goat eats the grass.")]},
    question_shot(SET6, RAJU, river(numbers=True), "Pehle kise le jaoge? Teen second!", "पहले किसे ले जाओगे? तीन सेकंड!",
                  "Which one goes first? Three seconds!"),
    {"set": SET6, "transition": "whoosh", "cast": RAJU, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.6,
     "overlay": river(trips=[("@L0+0.2", "goat", "R"), ("@L0+1.9", None, "L"),
                             ("@L1+0.2", "wolf", "R"), ("@L1+1.9", "goat", "L"),
                             ("@L2+0.2", "grass", "R"), ("@L2+1.9", None, "L"),
                             ("@L3+0.2", "goat", "R")]),
     "stamp": {"text": "SAB PAAR!", "on": "raju", "line": 3, "y": 1560, "w": 560},
     "lines": [ln("foxley", "Pehle bakri le jao, aur khaali wapas aao.", "पहले बकरी ले जाओ, और ख़ाली वापस आओ।",
                  "First take the goat, and come back empty.", sfx_before="reveal"),
               ln("foxley", "Phir bhediya le jao... aur bakri wapas le aao!", "फिर भेड़िया ले जाओ... और बकरी वापस ले आओ!",
                  "Then take the wolf... and bring the goat back!"),
               ln("foxley", "Ab ghaas le jao, aur khaali wapas aao.", "अब घास ले जाओ, और ख़ाली वापस आओ।", "Now take the grass, and come back empty."),
               ln("foxley", "Aakhir mein bakri! Sab salamat paar!", "आख़िर में बकरी! सब सलामत पार!", "Finally, the goat! Everyone across safely!")]},
    {"set": SET6, "cast": RAJU, "camera": cam(1.0, 1.0), "feet": 0.93, "overlay": river(), "hold": 0.6},
  ]}

# ===================================================================== 7. Do Matke
POTS = {"a": (130, 5, "5 LITRE"), "b": (620, 3, "3 LITRE")}   # x, capacity, label
POT_BOTTOM = PY + 380
UNIT = 52                                                    # px per litre


def matke(steps=(), ring_at=None):
    """steps: list of (time expr, {"a": litres, "b": litres}) to tween water levels to"""
    html = panel(PY - 10, 470, title="DO MATKE")
    js, sfx = [], []
    for k, (x, cap, label) in POTS.items():
        w, h = (300 if cap == 5 else 240), cap * UNIT + 20
        top = POT_BOTTOM - h
        html += (f'<div style="position:absolute;left:{x}px;top:{top}px;width:{w}px;height:{h}px;border:9px solid {INK};border-top:none;'
                 f'border-radius:0 0 90px 90px;background:#FFF5E6;overflow:hidden">'
                 f'<div id="{{sid}}-w{k}" style="position:absolute;left:0;right:0;bottom:0;height:0px;background:linear-gradient(#7FD3F7,#2E8BC0)"></div></div>'
                 f'<div style="position:absolute;left:{x - 14}px;top:{top - 22}px;width:{w + 28}px;height:30px;background:#B5651D;border:7px solid {INK};border-radius:14px"></div>'
                 f'<div style="position:absolute;left:{x}px;width:{w}px;top:{POT_BOTTOM + 14}px;text-align:center;font-weight:900;font-size:36px;color:{INK}">{label}</div>')
        for v in range(cap + 1):
            html += (f'<div id="{{sid}}-n{k}{v}" style="position:absolute;left:{x + w + 10}px;top:{top - 10}px;font-weight:900;font-size:48px;color:#1F4E5F;'
                     f'opacity:{1 if v == 0 else 0}">{v} L</div>')
    cur = {"a": 0, "b": 0}
    for t, state in steps:
        for k, v in state.items():
            if v == cur[k]:
                continue
            js.append(f'tl.to("#{{sid}}-w{k}", {{height: {v * UNIT}, duration: 0.8, ease: "power1.inOut"}}, {t});')
            js.append(f'tl.set("#{{sid}}-n{k}{cur[k]}", {{opacity: 0}}, {t}+0.8); tl.set("#{{sid}}-n{k}{v}", {{opacity: 1}}, {t}+0.8);')
            cur[k] = v
        sfx.append(["whoosh", t])
    if ring_at:
        html += (f'<div id="{{sid}}-ring" style="position:absolute;left:100px;top:{PY + 40}px;width:420px;height:430px;border:10px solid #C8342B;'
                 f'border-radius:50%;opacity:0"></div>') + tag("THIK 4 LITRE!", 160, PY + 6, "four")
        js += [pop("ring", ring_at), pop("four", f"{ring_at}+0.3")]
        sfx.append(["reveal", ring_at])
    return ov(html, js, sfx)


SET7 = set_or("desert_village", "kitchen")
RAFIQ = [{"id": "rafiq", "x": 0.5}]
EPS["riddle_matke"] = {"number": 307, "part": 1, "slug": "riddle_matke", "title": {"ur": "DO MATKE", "en": "TWO POTS"},
  "handle": "@AskFoxley", "music": {"bpm": 100, "gain": 0.5},
  "answer_note": "Fill 5; pour into 3 (2 left); empty 3; pour the 2 in; fill 5; top up 3 -> 4 left in the 5.",
  "shots": [
    {"set": SET7, "cast": RAFIQ, "camera": cam(), "feet": 0.93, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1,
     "hook": {"text": "THIK 4 LITRE... SIRF DO MATKON SE!", "y": 110, "dur": 99}, "overlay": matke(),
     "lines": [ln("rafiq", "Mujhe thik chaar litre paani chahiye. Matke sirf paanch aur teen litre ke hain!",
                  "मुझे ठीक चार लीटर पानी चाहिए। मटके सिर्फ़ पाँच और तीन लीटर के हैं!",
                  "I need exactly four litres of water. The pots only hold five and three litres!")]},
    question_shot(SET7, RAFIQ, matke(), "Kaise naapoge thik chaar litre? Socho!", "कैसे नापोगे ठीक चार लीटर? सोचो!",
                  "How do you measure exactly four litres? Think!", main="KAISE NAAPOGE? COMMENT KARO!"),
    {"set": SET7, "transition": "whoosh", "cast": RAFIQ, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.6,
     "overlay": matke(steps=[("@L0+0.4", {"a": 5}), ("@L1+0.5", {"a": 2, "b": 3}), ("@L2+0.3", {"b": 0}), ("@L2+2.0", {"a": 0, "b": 2}),
                             ("@L3+0.3", {"a": 5}), ("@L3+2.0", {"a": 4, "b": 3})], ring_at="@L4+0.3"),
     "stamp": {"text": "KAMAAL!", "on": "rafiq", "line": 4, "y": 1560},
     "lines": [ln("foxley", "Paanch wala bharo.", "पाँच वाला भरो।", "Fill the five.", sfx_before="reveal"),
               ln("foxley", "Usse teen wala bharo. Paanch mein bache do.", "उससे तीन वाला भरो। पाँच में बचे दो।", "Fill the three from it. Two are left in the five."),
               ln("foxley", "Teen wala khaali karo, aur woh do litre usmein daalo.", "तीन वाला ख़ाली करो, और वो दो लीटर उसमें डालो।",
                  "Empty the three, and pour those two litres into it."),
               ln("foxley", "Paanch wala phir bharo, aur teen wale ko upar tak bharo.", "पाँच वाला फिर भरो, और तीन वाले को ऊपर तक भरो।",
                  "Fill the five again, and top up the three."),
               ln("rafiq", "Waah! Paanch wale mein bache thik chaar!", "वाह! पाँच वाले में बचे ठीक चार!", "Wow! Exactly four left in the five!")]},
    {"set": SET7, "cast": RAFIQ, "camera": cam(1.0, 1.0), "feet": 0.93, "overlay": matke(), "hold": 0.6},
  ]}

# ===================================================================== 8. Pehredaar
SUN = ('<svg viewBox="0 0 200 200" width="100%" height="100%"><rect width="200" height="200" fill="#8FD3F4"/>'
       '<path d="M0 150 q50 -30 100 0 q50 30 100 0 v50 h-200z" fill="#7CB342" stroke="#2B2B2B" stroke-width="4"/>'
       '<circle cx="100" cy="78" r="34" fill="#F2B134" stroke="#2B2B2B" stroke-width="5"/>'
       + "".join(f'<path d="M{100 + 46 * math.cos(a / 10 * 6.283):.0f} {78 + 46 * math.sin(a / 10 * 6.283):.0f} L{100 + 60 * math.cos(a / 10 * 6.283):.0f} {78 + 60 * math.sin(a / 10 * 6.283):.0f}" stroke="#E8762B" stroke-width="6" stroke-linecap="round"/>' for a in range(10))
       + '</svg>')


def lion_svg():
    mane = "".join(f'<circle cx="{100 + 70 * math.cos(a / 12 * 6.283):.1f}" cy="{106 + 70 * math.sin(a / 12 * 6.283):.1f}" r="26" fill="#B5651D" stroke="#2B2B2B" stroke-width="5"/>' for a in range(12))
    return ('<svg viewBox="0 0 200 200" width="100%" height="100%"><rect width="200" height="200" fill="#5A3A1E"/>' + mane +
            '<circle cx="100" cy="106" r="62" fill="#F2B134" stroke="#2B2B2B" stroke-width="5"/>'
            '<circle cx="84" cy="98" r="8" fill="#2B2B2B"/><circle cx="118" cy="98" r="8" fill="#2B2B2B"/>'
            '<path d="M92 116 h18 l-9 10z" fill="#5A2E14" stroke="#2B2B2B" stroke-width="4"/>'
            '<path d="M80 134 q20 26 42 0" fill="#C8342B" stroke="#2B2B2B" stroke-width="5"/></svg>')


DOORS2 = [(110, 1), (630, 2)]


def gate(open_at=None, show_back=False):
    html, js, sfx = "", [], []
    for x, n in DOORS2:
        behind = SUN if n == 1 else lion_svg()
        lbl = "AZAADI" if n == 1 else "BHOOKA SHER"
        html += (f'<div style="position:absolute;left:{x}px;top:{PY}px;width:340px;height:440px;border:10px solid {INK};border-radius:170px 170px 10px 10px;'
                 f'overflow:hidden;background:#3A2410;box-shadow:0 12px 0 {INK}">'
                 f'<div style="position:absolute;left:30px;right:30px;top:90px;bottom:40px">{behind}</div>'
                 f'<div id="{{sid}}-door{n}" style="position:absolute;inset:0;background:linear-gradient(90deg,#6B3F22,#8A5A2B,#6B3F22);transform-origin:0 50%;'
                 f'{"opacity:0;" if show_back else ""}">'
                 f'<div style="position:absolute;left:50%;top:150px;margin-left:-60px;font-weight:900;font-size:150px;color:#F2B134;text-shadow:0 6px 0 {INK}">?</div></div></div>'
                 + badge(n, x + 140, PY - 36, 70, 44)
                 + tag(lbl, x + 30, PY + 450, f"lb{n}", bg="#2E9E4F" if n == 1 else "#C8342B"))
        if show_back:
            js.append(pop(f"lb{n}", "@S+0.2"))
    if open_at:
        js += [f'tl.to("#{{sid}}-door1", {{scaleX: 0.05, duration: 0.6, ease: "power2.inOut"}}, {open_at});',
               pop("lb1", f"{open_at}+0.6"),
               f'tl.to("#{{sid}}-door2", {{scaleX: 0.05, duration: 0.6, ease: "power2.inOut"}}, {open_at}+1.6);',
               pop("lb2", f"{open_at}+2.2")]
        sfx += [["reveal", open_at], ["sting", f"{open_at}+1.6"]]
    return ov(html, js, sfx)


def logic_card(at):
    rows = [("AGAR SACHCHE SE POOCHA:", "woh jhoote ka galat jawab batayega"),
            ("AGAR JHOOTE SE POOCHA:", "woh sachche ka jawab ulta karega"),
            ("DONO BAAR:", "GALAT darwaza! To ulta chuno")]
    html = panel(PY - 10, 470, title="KYUN?")
    js = []
    for i, (a, b) in enumerate(rows):
        html += (f'<div id="{{sid}}-row{i}" style="position:absolute;left:80px;right:80px;top:{PY + 40 + i * 140}px;opacity:0">'
                 f'<div style="font-weight:900;font-size:40px;color:{"#C8342B" if i == 2 else "#1F4E5F"}">{a}</div>'
                 f'<div style="font-weight:800;font-size:44px;color:{INK}">{b}</div></div>')
        js.append(pop(f"row{i}", f"{at[i]}"))
    return ov(html, js, [["pop", at[0]]])


SET8 = set_or("qila_gate", "police_station")
TRIO8 = [{"id": "sherkhan", "x": 0.2}, {"id": "bunty", "x": 0.5}, {"id": "bilal", "x": 0.8}]
EPS["riddle_pehredaar"] = {"number": 308, "part": 1, "slug": "riddle_pehredaar", "title": {"ur": "SACH AUR JHOOTH", "en": "TRUTH AND LIES"},
  "handle": "@AskFoxley", "music": {"bpm": 98, "gain": 0.5},
  "answer_note": "Ask either guard which door the OTHER guard would call the way out, then take the opposite door.",
  "shots": [
    {"set": SET8, "cast": TRIO8, "camera": cam(), "feet": 0.95, "sfx": [["sting", 0.0]], "caption_y": 1300, "hold": 0.1,
     "hook": {"text": "EK SAWAAL... AUR ZINDAGI KA FAISLA!", "y": 110, "dur": 99}, "overlay": gate(),
     "lines": [ln("foxley", "Ek darwaza azaadi ka, doosra bhooke sher ka.", "एक दरवाज़ा आज़ादी का, दूसरा भूखे शेर का।",
                  "One door leads to freedom, the other to a hungry lion.")]},
    {"set": SET8, "transition": "whoosh", "cast": TRIO8, "camera": cam(), "feet": 0.95, "caption_y": 1300, "hold": 0.2, "overlay": gate(),
     "lines": [ln("foxley", "Ek pehredaar hamesha sach bolta hai, doosra hamesha jhoot. Kaun kaun hai, koi nahi jaanta!",
                  "एक पहरेदार हमेशा सच बोलता है, दूसरा हमेशा झूठ। कौन कौन है, कोई नहीं जानता!",
                  "One guard always tells the truth, the other always lies. Nobody knows which is which!")]},
    question_shot(SET8, TRIO8, gate(), "Sirf ek sawaal! Kya poochoge?", "सिर्फ़ एक सवाल! क्या पूछोगे?", "Just one question! What would you ask?",
                  main="KYA POOCHOGE? COMMENT KARO!", feet=0.95, caption_y=1300),
    {"set": SET8, "transition": "whoosh", "cast": [{"id": "bunty", "x": 0.32}, {"id": "sherkhan", "x": 0.7}],
     "camera": {"from": {"focus": "group", "zoom": 1.2}, "to": {"focus": "group", "zoom": 1.28}}, "hold": 0.3,
     "lines": [ln("bunty", "Agar main doosre pehredaar se poochoon ke azaadi ka darwaza kaunsa hai, to woh kya batayega?",
                  "अगर मैं दूसरे पहरेदार से पूछूँ के आज़ादी का दरवाज़ा कौनसा है, तो वो क्या बताएगा?",
                  "If I asked the other guard which door leads to freedom, what would he say?"),
               ln("sherkhan", "Woh darwaza number do batayega!", "वो दरवाज़ा नंबर दो बताएगा!", "He would say door number two!")]},
    {"set": SET8, "transition": "whoosh", "cast": TRIO8, "camera": cam(), "feet": 0.95, "caption_y": 1300, "hold": 0.4,
     "overlay": gate(open_at="@L0+0.6"),
     "stamp": {"text": "BACH GAYA!", "on": "bunty", "line": 1, "y": 130, "w": 640},
     "lines": [ln("foxley", "To darwaza number ek kholo!", "तो दरवाज़ा नंबर एक खोलो!", "So open door number one!", sfx_before="reveal"),
               ln("bunty", "Azaadi! Main bach gaya!", "आज़ादी! मैं बच गया!", "Freedom! I'm saved!")]},
    {"set": SET8, "transition": "whoosh", "cast": TRIO8, "camera": cam(), "feet": 0.95, "caption_y": 230, "hold": 0.5,
     "overlay": logic_card(["@L0+0.3", "@L0+2.2", "@L1+0.3"]),
     "lines": [ln("foxley", "Sachcha jhoote ka jawab sach bataata hai, aur jhoota sachche ka jawab ulta kar deta hai.",
                  "सच्चा झूठे का जवाब सच बताता है, और झूठा सच्चे का जवाब उल्टा कर देता है।",
                  "The truthful one reports the liar's answer honestly, and the liar flips the truthful one's answer."),
               ln("foxley", "Dono soorat mein jawab galat darwaze ka. Isliye ulta chuno!", "दोनों सूरत में जवाब ग़लत दरवाज़े का। इसलिए उल्टा चुनो!",
                  "Either way, the answer is the wrong door. So pick the other one!")]},
    {"set": SET8, "cast": TRIO8, "camera": cam(1.0, 1.0), "feet": 0.95, "overlay": gate(), "hold": 0.6},
  ]}

# ===================================================================== 9. Kaunsi Balti Pehle Bharegi
PIPES = [
    [(540, 700), (540, 760), (300, 760), (300, 860), (170, 860), (170, 1230)],                       # to bucket 1
    [(300, 860), (430, 860), (430, 960), (540, 960), (540, 1230)],                                    # to bucket 2
    [(540, 760), (780, 760), (780, 1100), (910, 1100), (910, 1230)],                                  # to bucket 3
]
ROUTES = {  # water routes from the tank; end = block point or bucket
    1: ([(540, 700), (540, 760), (300, 760), (300, 860), (170, 860), (170, 1010)], "block"),
    2: ([(540, 700), (540, 760), (300, 760), (300, 860), (430, 860), (430, 960), (540, 960), (540, 1230)], "bucket"),
    3: ([(540, 700), (540, 760), (780, 760), (780, 850)], "block"),
}
BLOCKS = [(170, 1030), (780, 870)]
BUCKETS = {1: 170, 2: 540, 3: 910}


def plen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def pts_attr(pts):
    return " ".join(f"{x},{y}" for x, y in pts)


def pipes(flow_at=None):
    svg = f'<svg viewBox="0 0 1080 1920" width="1080" height="1920" style="position:absolute;left:0;top:0">'
    svg += f'<rect x="420" y="560" width="240" height="150" rx="18" fill="#2B2B2B"/><rect x="436" y="576" width="208" height="20" rx="8" fill="#555"/>'
    for p in PIPES:
        svg += f'<polyline points="{pts_attr(p)}" fill="none" stroke="{INK}" stroke-width="40" stroke-linejoin="round" stroke-linecap="round"/>'
    for p in PIPES:
        svg += f'<polyline points="{pts_attr(p)}" fill="none" stroke="#B0B0B0" stroke-width="26" stroke-linejoin="round" stroke-linecap="round"/>'
    for k, (x, y) in enumerate(BLOCKS):   # closed valves: a red wheel and a dark plug across the pipe
        svg += (f'<rect x="{x - 26}" y="{y - 12}" width="52" height="24" rx="6" fill="{INK}"/>'
                f'<circle cx="{x + 40}" cy="{y}" r="20" fill="#C8342B" stroke="{INK}" stroke-width="5"/><path d="M{x + 26} {y} h28 M{x + 40} {y - 14} v28" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M{x + 20} {y} h-0" stroke="{INK}" stroke-width="5"/>')
    js, sfx = [], []
    if flow_at:
        for n, (pts, end) in ROUTES.items():
            L = plen(pts)
            svg += (f'<polyline id="{{sid}}-wf{n}" points="{pts_attr(pts)}" fill="none" stroke="#2E8BC0" stroke-width="14" stroke-linejoin="round" stroke-linecap="round" '
                    f'style="stroke-dasharray:{L:.0f};stroke-dashoffset:{L:.0f}"/>')
            js.append(f'tl.to("#{{sid}}-wf{n}", {{strokeDashoffset: 0, duration: {L / 420:.2f}, ease: "none"}}, {flow_at});')
            if end == "block":
                js.append(pop(f"x{n}", f"{flow_at}+{L / 420:.2f}"))
                sfx.append(["stamp", f"{flow_at}+{L / 420:.2f}"])
        js.append(f'tl.to("#{{sid}}-fill2", {{height: 120, duration: 1.2, ease: "power1.inOut"}}, {flow_at}+{plen(ROUTES[2][0]) / 420:.2f});')
        sfx.append(["whoosh", flow_at])
    svg += "</svg>"
    html = svg
    for n, x in BUCKETS.items():
        html += (f'<div style="position:absolute;left:{x - 90}px;top:1236px;width:180px;height:150px;border:9px solid {INK};border-radius:6px 6px 40px 40px;'
                 f'background:#FFF5E6;overflow:hidden"><div id="{{sid}}-fill{n}" style="position:absolute;left:0;right:0;bottom:0;height:0;background:#2E8BC0"></div></div>'
                 + badge(n, x - 35, 1400, 70, 44))
    for n in (1, 3):
        x, y = BLOCKS[0] if n == 1 else BLOCKS[1]
        html += tag("BAND!", x - 70, y - 90, f"x{n}")
    return ov(html, js, sfx)


SET9 = set_or("chhat_rooftop", "gali_street")
EPS["riddle_balti"] = {"number": 309, "part": 1, "slug": "riddle_balti", "title": {"ur": "KAUNSI BALTI?", "en": "WHICH BUCKET?"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5},
  "answer_note": "Bucket 2: the pipes to buckets 1 and 3 have closed valves.",
  "shots": [
    {"set": SET9, "dark": 0.25, "cast": [], "camera": cam(1.0, 1.0), "sfx": [["sting", 0.0]], "caption_y": 1480, "hold": 0.1,
     "hook": {"text": "SIRF 1% LOG PEHLI BAAR MEIN SAHI!", "y": 110, "dur": 99}, "overlay": pipes(),
     "lines": [ln("foxley", "Tanki khul gayi! Kaunsi balti sab se pehle bharegi?", "टंकी खुल गई! कौनसी बाल्टी सब से पहले भरेगी?",
                  "The tank is open! Which bucket fills first?")]},
    {"set": SET9, "dark": 0.25, "cast": [], "camera": cam(1.0, 1.0), "overlay": pipes(), "timer": 5, "timer_y": 1500, "sfx": [["riser", 0.0]],
     "cta": {"after_timer": True, "y": 160, "main": "1, 2 YA 3? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."}, "hold": 0.6,
     "hook": {"text": "PAUSE KARO AUR PIPE DEKHO!", "y": 110, "dur": 99}, "lines": []},
    {"set": SET9, "dark": 0.25, "cast": [], "camera": cam(1.0, 1.0), "overlay": pipes(flow_at="@L0+0.3"), "caption_y": 230, "hold": 0.6,
     "stamp": {"text": "BALTI 2!", "on": None, "line": 1, "y": 1560, "w": 520},
     "lines": [ln("foxley", "Paani ka raasta dekho!", "पानी का रास्ता देखो!", "Follow the water!", sfx_before="reveal"),
               ln("foxley", "Ek aur teen ke pipe band hain. Sirf do bharegi!", "एक और तीन के पाइप बंद हैं। सिर्फ़ दो भरेगी!",
                  "The pipes to one and three are closed. Only two fills!")]},
    {"set": SET9, "dark": 0.25, "cast": [], "camera": cam(1.0, 1.0), "overlay": pipes(), "hold": 0.6},
  ]}

for name, ep in EPS.items():
    json.dump(ep, open(os.path.join(ROOT, "episodes", f"{name}.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote episodes/%s.json (set: %s)" % (name, ep["shots"][0]["set"]))
