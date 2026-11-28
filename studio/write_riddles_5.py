"""Writes riddles 10-17 of planning/NEW_RIDDLES_2.md (2026-11-28), props drawn in code:

  riddle_bulb      Teen Bulb           apartment_lobby / apartment_hallway
  riddle_rang      Geela Rang          town_park
  riddle_umar      Umar Ki Paheli      garden
  riddle_moze      Andhere Mein Moze   small_bedroom
  riddle_pul       Raat Ka Pul         raat_pul
  riddle_kuan      Kuen Ka Paani       desert_village
  riddle_shikari   Teen Shikari        river_ghat
  riddle_glass     Chhe Glass          kitchen

    python3 studio/write_riddles_5.py
"""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2B2B2B"
W, H = 1080, 1920
PY = 600
BASE_H = 0.34


def ln(who, cap, say, en, **k):
    return {"who": who, "caption": cap, "say": say, "en": en, **k}


def ov(html, js=(), sfx=()):
    return {"html": html, "js": list(js), "sfx": [list(s) for s in sfx]}


def panel(top, h, title=None, bg="rgba(255,248,230,0.94)", left=40, right=40):
    t = (f'<div style="position:absolute;left:0;right:0;top:-34px;text-align:center"><span style="background:#1F4E5F;color:#fff;font-weight:900;'
         f'font-size:36px;padding:4px 24px;border:6px solid {INK};border-radius:18px">{title}</span></div>') if title else ""
    return (f'<div style="position:absolute;left:{left}px;right:{right}px;top:{top}px;height:{h}px;background:{bg};border:8px solid {INK};'
            f'border-radius:30px;box-shadow:0 12px 0 {INK}">{t}</div>')


def badge(n, x, y, size=60, fs=38):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;border-radius:50%;background:#F2B134;'
            f'border:6px solid {INK};display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{fs}px;color:{INK};z-index:3">{n}</div>')


def tag(text, x, y, idx=None, bg="#C8342B", fs=34, hidden=True, center=False):
    i = f' id="{{sid}}-{idx}"' if idx else ""
    tr = "transform:translateX(-50%);" if center else ""
    return (f'<div{i} style="position:absolute;left:{x}px;top:{y}px;{tr}background:{bg};color:#fff;font-weight:900;font-size:{fs}px;'
            f'white-space:nowrap;padding:4px 16px;border:5px solid {INK};border-radius:16px;{"opacity:0;" if (idx and hidden) else ""}z-index:4">{text}</div>')


def big(text, x, y, idx, color="#C8342B", fs=120):
    return (f'<div id="{{sid}}-{idx}" style="position:absolute;left:{x}px;top:{y}px;transform:translateX(-50%);font-weight:900;font-size:{fs}px;color:{color};'
            f'opacity:0;text-shadow:-6px -6px 0 #fff,6px -6px 0 #fff,-6px 6px 0 #fff,6px 6px 0 #fff,0 10px 0 {INK};white-space:nowrap">{text}</div>')


def pop(idx, t):
    return f'tl.fromTo("#{{sid}}-{idx}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t});'


def show(idx, t):
    return f'tl.set("#{{sid}}-{idx}", {{opacity: 1}}, {t});'


def hide(idx, t):
    return f'tl.set("#{{sid}}-{idx}", {{opacity: 0}}, {t});'


def cam(z0=1.0, z1=1.03, fy=0.62):
    return {"from": {"focus": [0.5, fy], "zoom": z0}, "to": {"focus": [0.5, fy], "zoom": z1}}


STILL = cam(1.0, 1.0)


def rig(cid):
    return json.load(open(os.path.join(ROOT, "puppet", "cast", cid, "rig.json")))


def head_top(cid, x_frac, feet=0.87):
    """frame position (x, y) of the top of a character's head at camera zoom 1.0 (same maths as build_story)"""
    return x_frac * W, H * feet - H * BASE_H * rig(cid)["height"]


def hook_shot(set_, cast, hook, line, overlay=None, **k):
    sh = {"set": set_, "cast": cast, "camera": cam(), "feet": 0.93, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1,
          "hook": {"text": hook, "y": 110, "dur": 99}, "lines": line if isinstance(line, list) else [line]}
    if overlay: sh["overlay"] = overlay
    sh.update(k)
    return sh


def question(set_, cast, overlay, text, say, en, main="1, 2 YA 3? COMMENT KARO!", **k):
    sh = {"set": set_, "transition": "whoosh", "cast": cast, "camera": cam(), "feet": 0.93, "timer": 3, "timer_y": 1500,
          "caption_y": 1290, "sfx": [["riser", 0.0]], "hold": 0.6,
          "cta": {"after_timer": True, "y": 160, "main": main, "sub": "Jawab abhi aa raha hai..."}, "lines": [ln("foxley", text, say, en)]}
    if overlay: sh["overlay"] = overlay
    sh.update(k)
    return sh


def loop_shot(first):
    """the last shot repeats the first one's picture (no hook, no lines) so the Reel loops"""
    sh = {k: v for k, v in first.items() if k not in ("hook", "lines", "sfx", "caption_y", "hold", "transition")}
    sh["camera"] = {"from": first["camera"]["from"], "to": first["camera"]["from"]}
    sh["hold"] = 0.6
    if "overlay" in first:
        sh["overlay"] = {"html": first["overlay"]["html"], "js": [], "sfx": []}
    return sh


EPS = {}

# ===================================================================== 10. Teen Bulb
def switch(n, x, y, on_at=None, off_at=None, start_on=False):
    h = (f'<div style="position:absolute;left:{x}px;top:{y}px;width:110px;height:170px;background:#F5F1E8;border:7px solid {INK};border-radius:18px">'
         f'<div id="{{sid}}-sw{n}" style="position:absolute;left:30px;top:{24 if start_on else 76}px;width:36px;height:56px;background:{"#2E9E4F" if start_on else "#9E9E9E"};'
         f'border:5px solid {INK};border-radius:10px"></div></div>' + badge(n, x + 25, y + 180, 56, 34))
    js = []
    if on_at:
        js.append(f'tl.to("#{{sid}}-sw{n}", {{top: 24, backgroundColor: "#2E9E4F", duration: 0.15}}, {on_at});')
    if off_at:
        js.append(f'tl.to("#{{sid}}-sw{n}", {{top: 76, backgroundColor: "#9E9E9E", duration: 0.15}}, {off_at});')
    return h, js


def bulb(k, x, y, state=None, at=None):
    """state: 'lit' | 'warm' | 'cold'"""
    glow = (f'<div id="{{sid}}-glow{k}" style="position:absolute;left:{x - 60}px;top:{y - 60}px;width:240px;height:240px;border-radius:50%;'
            f'background:radial-gradient(rgba(255,230,120,0.95),rgba(255,230,120,0) 70%);opacity:0"></div>')
    body = (f'<div style="position:absolute;left:{x}px;top:{y}px;width:120px;height:170px"><svg viewBox="0 0 120 170" width="100%" height="100%">'
            f'<g stroke="{INK}" stroke-width="6" stroke-linejoin="round"><path id="{{sid}}-bulbfill{k}" d="M60 8 C20 8 6 40 14 70 C20 92 36 100 38 122 H82 C84 100 100 92 106 70 C114 40 100 8 60 8Z" fill="#EEF3F6"/>'
            f'<rect x="38" y="122" width="44" height="34" rx="6" fill="#9E9E9E"/></g></svg></div>')
    heat = (f'<div id="{{sid}}-heat{k}" style="position:absolute;left:{x + 10}px;top:{y - 70}px;width:100px;height:60px;opacity:0">'
            f'<svg viewBox="0 0 100 60" width="100%" height="100%"><path d="M20 55 q-10 -12 0 -24 q10 -12 0 -26 M50 55 q-10 -12 0 -24 q10 -12 0 -26 M80 55 q-10 -12 0 -24 q10 -12 0 -26" '
            f'fill="none" stroke="#E8432B" stroke-width="6" stroke-linecap="round"/></svg></div>')
    js = []
    if state == "lit":
        js += [f'tl.to("#{{sid}}-glow{k}", {{opacity: 1, duration: 0.3}}, {at});', f'tl.to("#{{sid}}-bulbfill{k}", {{attr: {{fill: "#FFE066"}}, duration: 0.2}}, {at});']
    if state == "warm":
        js += [f'tl.fromTo("#{{sid}}-heat{k}", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.4}}, {at});',
               f'tl.to("#{{sid}}-heat{k}", {{y: -8, duration: 0.5, yoyo: true, repeat: 5, ease: "sine.inOut"}}, {at}+0.4);']
    return glow + body + heat, js


def bulb_board(switch_steps=None, bulb_steps=None):
    """left: three switches (downstairs); right: three bulbs (upstairs)"""
    html = panel(PY - 10, 480, "NEECHE SWITCH · UPAR BULB")
    js, sfx = [], []
    ss = switch_steps or {}
    for n, x in ((1, 80), (2, 210), (3, 340)):
        h, j = switch(n, x, PY + 60, **ss.get(n, {}))
        html += h; js += j
    html += (f'<div style="position:absolute;left:470px;top:{PY + 120}px;font-size:80px;font-weight:900;color:{INK}">&#10140;</div>')
    bs = bulb_steps or {}
    for k, x in ((1, 590), (2, 740), (3, 890)):
        st, at = bs.get(k, (None, None))
        h, j = bulb(k, x - 30, PY + 100, st, at)
        html += h; js += j
    return html, js, sfx


def bulbs_overlay(switch_steps=None, bulb_steps=None, labels_at=None, clock_at=None):
    html, js, sfx = bulb_board(switch_steps, bulb_steps)
    if clock_at:
        html += tag("5 MINUTE RUKO...", 120, PY + 300, "clk", bg="#1F4E5F")
        js.append(pop("clk", clock_at)); sfx.append(["tick", clock_at])
    if labels_at:
        for k, (x, txt, col) in enumerate(((620, "SW 1", "#E8762B"), (770, "SW 2", "#2E9E4F"), (920, "SW 3", "#1F4E5F"))):
            html += tag(txt, x, PY + 300, f"lb{k}", bg=col, fs=30, center=True)
            js.append(pop(f"lb{k}", labels_at[k]))
    for n, d in (switch_steps or {}).items():
        for key in ("on_at", "off_at"):
            if key in d: sfx.append(["pop", d[key]])
    return ov(html, js, sfx)


RAJU = [{"id": "raju", "x": 0.5}]
b0 = hook_shot("apartment_lobby", RAJU, "SIRF EK BAAR UPAR JA SAKTE HO!",
               [ln("raju", "Neeche teen switch, upar teen bulb. Kaunsa switch kis bulb ka hai?", "नीचे तीन स्विच, ऊपर तीन बल्ब। कौनसा स्विच किस बल्ब का है?",
                   "Three switches down here, three bulbs upstairs. Which switch is which bulb?"),
                ln("foxley", "Aur upar sirf ek baar ja sakte ho!", "और ऊपर सिर्फ़ एक बार जा सकते हो!", "And you can only go upstairs once!")],
               overlay=bulbs_overlay())
EPS["riddle_bulb"] = {"number": 310, "part": 1, "slug": "riddle_bulb", "title": {"ur": "TEEN BULB", "en": "THREE BULBS"},
  "handle": "@AskFoxley", "music": {"bpm": 102, "gain": 0.5},
  "answer_note": "Switch 1 on for 5 minutes then off, switch 2 on, go up: lit = 2, warm = 1, cold = 3.",
  "shots": [
    b0,
    question("apartment_lobby", RAJU, bulbs_overlay(), "Kaise pata karoge? Teen second!", "कैसे पता करोगे? तीन सेकंड!", "How do you find out? Three seconds!",
             main="KAISE? COMMENT KARO!"),
    {"set": "apartment_lobby", "transition": "whoosh", "cast": RAJU, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.3,
     "overlay": bulbs_overlay(switch_steps={1: {"on_at": "@L0+0.4", "off_at": "@L0+2.8"}, 2: {"on_at": "@L1+0.4"}}, clock_at="@L0+1.0"),
     "lines": [ln("foxley", "Switch ek on karo, paanch minute ruko, phir off kar do.", "स्विच एक ऑन करो, पाँच मिनट रुको, फिर ऑफ़ कर दो।",
                  "Turn switch one on, wait five minutes, then turn it off.", sfx_before="reveal"),
               ln("foxley", "Ab switch do on karo, aur upar jao.", "अब स्विच दो ऑन करो, और ऊपर जाओ।", "Now turn switch two on, and go upstairs.")]},
    {"set": "apartment_hallway", "transition": "whoosh", "cast": RAJU, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.5,
     "overlay": bulbs_overlay(switch_steps={2: {}}, bulb_steps={2: ("lit", "@L0+0.2"), 1: ("warm", "@L1+0.2")},
                              labels_at=["@L1+0.6", "@L0+0.6", "@L2+0.4"]),
     "stamp": {"text": "KAMAAL!", "on": "raju", "line": 3, "y": 1560},
     "lines": [ln("foxley", "Jo bulb jal raha hai, woh switch do ka.", "जो बल्ब जल रहा है, वो स्विच दो का।", "The bulb that's on is switch two."),
               ln("foxley", "Jo bujha hai par garam, woh switch ek ka!", "जो बुझा है पर गरम, वो स्विच एक का!", "The one that's off but warm is switch one!"),
               ln("foxley", "Aur jo thanda hai, woh teen!", "और जो ठंडा है, वो तीन!", "And the cold one is three!"),
               ln("raju", "Waah! Ek hi chakkar mein!", "वाह! एक ही चक्कर में!", "Wow! In just one trip!")]},
    loop_shot(b0),
  ]}

# ===================================================================== 11. Geela Rang
def bench_card():
    return (panel(PY - 10, 300, "TAAZA RANG!") +
            f'<div style="position:absolute;left:250px;top:{PY + 40}px;width:580px;height:220px"><svg viewBox="0 0 580 220" width="100%" height="100%">'
            f'<g stroke="{INK}" stroke-width="7" stroke-linejoin="round"><rect x="30" y="30" width="520" height="36" rx="8" fill="#2E9E4F"/>'
            f'<rect x="30" y="80" width="520" height="36" rx="8" fill="#2E9E4F"/><rect x="20" y="128" width="540" height="30" rx="8" fill="#2E9E4F"/>'
            f'<path d="M60 158 v50 M520 158 v50" stroke-width="14"/></g>'
            f'<path d="M150 66 q4 14 0 22 M300 116 q4 14 0 22 M420 66 q4 16 0 24" stroke="#2E9E4F" stroke-width="10" stroke-linecap="round" fill="none"/></svg></div>'
            f'<div style="position:absolute;left:70px;top:{PY + 70}px;width:160px;height:150px;background:#FFF5DC;border:6px solid {INK};border-radius:12px;'
            f'transform:rotate(-6deg);display:flex;align-items:center;justify-content:center;text-align:center;font-weight:900;font-size:34px;color:#C8342B">TAAZA<br>RANG!<br>&#9888;</div>')


def stripes(x, y, at=None):
    """green paint stripes on a pair of trousers (frame position of the thighs)"""
    h = (f'<div id="{{sid}}-paint" style="position:absolute;left:{x}px;top:{y}px;width:150px;height:60px">'
         f'<svg viewBox="0 0 150 60" width="100%" height="100%"><path d="M6 10 h60 M84 10 h60 M6 34 h60 M84 34 h60" stroke="#2EC46A" stroke-width="10" stroke-linecap="round"/></svg></div>')
    js, sfx = [], []
    if at:
        h += (f'<div id="{{sid}}-ring" style="position:absolute;left:{x - 50}px;top:{y - 50}px;width:250px;height:160px;border:10px solid #C8342B;'
              f'border-radius:50%;opacity:0"></div>') + tag("HARA RANG!", x - 10, y + 120, "rl")
        js += [pop("ring", at), pop("rl", f"{at}+0.3")]
        sfx.append(["reveal", at])
    return h, js, sfx


SUSP11 = ["raju", "bunty", "faisal"]
PAINT_AT = (468, 1418)   # Faisal's thighs, close shot (fixed zoom 1.25); checked on a still
r0 = hook_shot("town_park", [{"id": "zara", "x": 0.5}], "TAAZA RANG NE CHOR PAKARWA DIYA!",
               ln("zara", "Main ne phone bench pe rakha tha... aur woh gayab!", "मैंने फ़ोन बेंच पे रखा था... और वो ग़ायब!",
                  "I left my phone on the bench... and it's gone!", after="shocked"), overlay=ov(bench_card()))


def alibi(cid, n, cap, say, en, **k):
    c = {"id": cid, "x": 0.5, "num": n}
    return {"set": "town_park", "transition": "whoosh", "cast": [c], "camera": {"from": {"focus": cid, "zoom": 1.25}, "to": {"focus": cid, "zoom": 1.25}},
            "hold": 0.3, "lines": [ln(cid, cap, say, en)], **k}


ph, pj, ps = stripes(*PAINT_AT)
ph2, pj2, ps2 = stripes(*PAINT_AT, at="@L0+0.3")
EPS["riddle_rang"] = {"number": 311, "part": 1, "slug": "riddle_rang", "title": {"ur": "GEELA RANG", "en": "WET PAINT"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5},
  "answer_note": "Faisal (3) says he never went near the bench, but there are fresh green stripes on his trousers.",
  "shots": [
    r0,
    alibi("raju", 1, "Main ne hi bench rang kiya tha... phir main gate pe chala gaya.", "मैंने ही बेंच रंग किया था... फिर मैं गेट पे चला गया।",
          "I painted the bench... then I went to the gate."),
    alibi("bunty", 2, "Main dhaabe pe samose kha raha tha!", "मैं ढाबे पे समोसे खा रहा था!", "I was eating samosas at the dhaba!"),
    alibi("faisal", 3, "Main to bench ke paas gaya hi nahi!", "मैं तो बेंच के पास गया ही नहीं!", "I never even went near the bench!", overlay=ov(ph)),
    question("town_park", [{"id": c, "x": x} for c, x in zip(SUSP11, (0.2, 0.5, 0.8))], ov(bench_card()), "Kaun jhoota? Teen second!",
             "कौन झूठा? तीन सेकंड!", "Who's lying? Three seconds!", lineup=SUSP11, lineup_at=0),
    {"set": "town_park", "transition": "whoosh", "cast": [{"id": "faisal", "x": 0.5, "pose": "nervous"}],
     "camera": {"from": {"focus": "faisal", "zoom": 1.25}, "to": {"focus": "faisal", "zoom": 1.25}}, "caption_y": 230, "hold": 0.5,
     "overlay": ov(ph2, pj2, ps2), "verdicts": [{"on": "faisal", "ok": False, "line": 1, "at": 0.1, "lift": 60}],
     "stamp": {"text": {"ur": "MUJRIM!", "en": "GUILTY!"}, "on": "faisal", "line": 2, "y": 1600},
     "lines": [ln("foxley", "Bench ke paas gaye hi nahi? To patloon pe hara rang kahan se aaya?", "बेंच के पास गए ही नहीं? तो पतलून पे हरा रंग कहाँ से आया?",
                  "Never went near the bench? Then where did the green paint on your trousers come from?", sfx_before="reveal"),
               ln("foxley", "Raju ke haath pe rang hona theek hai, woh painter hai!", "राजू के हाथ पे रंग होना ठीक है, वो पेंटर है!",
                  "Paint on Raju's hands is fine, he's the painter!"),
               ln("faisal", "Achha... phone main ne hi uthaya tha.", "अच्छा... फ़ोन मैंने ही उठाया था।", "Okay... I took the phone.", pose="guilty")]},
    loop_shot(r0),
  ]}

# ===================================================================== 12. Umar Ki Paheli
def age_card(answer_at=None):
    html = panel(PY - 10, 360, "UMAR")
    rows = [("JAB MAIN 6 KA THA", "BEHAN 3 KI"), ("AB MAIN 60 KA HOON", "BEHAN ?")]
    for i, (a, b) in enumerate(rows):
        y = PY + 50 + i * 130
        html += (f'<div style="position:absolute;left:90px;top:{y}px;font-weight:900;font-size:46px;color:#1F4E5F">{a}</div>'
                 f'<div style="position:absolute;right:90px;top:{y}px;font-weight:900;font-size:46px;color:{INK}">{b}</div>')
    js, sfx = [], []
    if answer_at:
        html += (f'<div id="{{sid}}-thirty" style="position:absolute;left:560px;top:{PY + 260}px;font-weight:900;font-size:70px;color:#9E9E9E;opacity:0">30?'
                 f'<svg viewBox="0 0 100 60" style="position:absolute;left:-10px;top:0;width:150px;height:90px"><path d="M5 50 L95 10" stroke="#C8342B" stroke-width="10"/></svg></div>')
        html += tag("FARQ HAMESHA 3 SAAL!", 90, PY + 270, "farq", bg="#1F4E5F", fs=36) + big("57!", 890, PY + 210, "ans", fs=130)
        js += [pop("thirty", answer_at), pop("farq", f"{answer_at}+1.0"), pop("ans", "@L1+0.8")]
        sfx += [["stamp", answer_at], ["reveal", "@L1+0.8"]]
    return ov(html, js, sfx)


JAMIL = [{"id": "jamil", "x": 0.5}]
u0 = hook_shot("garden", JAMIL, "90% LOG 30 BOLTE HAIN!",
               [ln("jamil", "Jab main chhe saal ka tha, meri behan meri aadhi umar ki thi.", "जब मैं छह साल का था, मेरी बहन मेरी आधी उम्र की थी।",
                   "When I was six, my sister was half my age."),
                ln("jamil", "Ab main saath saal ka hoon. Behan kitne saal ki hai?", "अब मैं साठ साल का हूँ। बहन कितने साल की है?",
                   "Now I'm sixty. How old is my sister?")], overlay=age_card())
EPS["riddle_umar"] = {"number": 312, "part": 1, "slug": "riddle_umar", "title": {"ur": "UMAR KI PAHELI", "en": "THE AGE RIDDLE"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5}, "answer_note": "57: she was 3 years younger, always.",
  "shots": [
    u0,
    question("garden", JAMIL, age_card(), "Jaldi bolo! Teen second!", "जल्दी बोलो! तीन सेकंड!", "Quick! Three seconds!", main="KITNE SAAL? COMMENT KARO!"),
    {"set": "garden", "transition": "whoosh", "cast": JAMIL, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.5,
     "overlay": age_card(answer_at="@L0+0.3"), "stamp": {"text": "57 SAAL!", "on": "jamil", "line": 2, "y": 1560, "w": 560},
     "lines": [ln("foxley", "Tees nahi! Behan tab bhi teen saal choti thi.", "तीस नहीं! बहन तब भी तीन साल छोटी थी।", "Not thirty! She was three years younger back then.", sfx_before="reveal"),
               ln("foxley", "Farq hamesha wohi rehta hai. Saath minus teen... sattawan!", "फ़र्क़ हमेशा वही रहता है। साठ माइनस तीन... सत्तावन!",
                  "The gap never changes. Sixty minus three... fifty-seven!"),
               ln("jamil", "Haan bhai! Behan sattawan ki hai!", "हाँ भाई! बहन सत्तावन की है!", "That's right! She's fifty-seven!")]},
    loop_shot(u0),
  ]}

# ===================================================================== 13. Andhere Mein Moze
def sock(color, x, y, idx=None, rot=0):
    i = f' id="{{sid}}-{idx}"' if idx else ""
    fill = INK if color == "k" else "#FFFFFF"
    return (f'<div{i} style="position:absolute;left:{x}px;top:{y}px;width:70px;height:90px;transform:rotate({rot}deg)">'
            f'<svg viewBox="0 0 70 90" width="100%" height="100%"><path d="M18 4 h30 v48 q0 10 10 14 q10 6 6 16 q-4 8 -20 6 h-20 q-16 -2 -14 -16 l8 -20z" '
            f'fill="{fill}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/><path d="M18 14 h30" stroke="#9E9E9E" stroke-width="5"/></svg></div>')


def drawer(pick_at=None):
    html = panel(PY - 10, 380, "10 KAALE · 10 SAFED")
    html += f'<div style="position:absolute;left:80px;top:{PY + 30}px;width:560px;height:300px;background:#6B3F22;border:8px solid {INK};border-radius:18px"></div>'
    for i in range(20):
        html += sock("k" if i % 2 == 0 else "w", 100 + (i % 7) * 74, PY + 50 + (i // 7) * 90, rot=(i * 37) % 30 - 15)
    html += (f'<div id="{{sid}}-dark" style="position:absolute;left:80px;top:{PY + 30}px;width:560px;height:300px;background:rgba(5,8,25,0.86);border-radius:18px;'
             f'display:flex;align-items:center;justify-content:center;font-weight:900;font-size:50px;color:#fff">ANDHERA</div>')
    js, sfx = [], []
    if pick_at:
        picks = [("k", 690, PY + 40), ("w", 800, PY + 40), ("k", 745, PY + 160)]
        for j, (c, x, y) in enumerate(picks):
            html += sock(c, x, y, idx=f"p{j}")
            js.append(pop(f"p{j}", f"{pick_at[j]}"))
            sfx.append(["pop", pick_at[j]])
        html += tag("JORA PAKKA!", 690, PY + 270, "jora", bg="#2E9E4F") + big("3", 950, PY + 120, "three", fs=150)
        js += [pop("jora", f"{pick_at[2]}+0.4"), pop("three", f"{pick_at[2]}+0.8")]
        sfx.append(["reveal", f"{pick_at[2]}+0.4"])
    return ov(html, js, sfx)


BUNTY = [{"id": "bunty", "x": 0.5}]
m0 = hook_shot("small_bedroom", BUNTY, "BIJLI GAYI... AUR MOZE KA JORA CHAHIYE!",
               [ln("foxley", "Andhera hai. Daraaz mein das kaale aur das safed moze hain.", "अँधेरा है। दराज़ में दस काले और दस सफ़ेद मोज़े हैं।",
                   "It's dark. The drawer has ten black and ten white socks."),
                ln("bunty", "Kam se kam kitne nikaaloon ke ek jora pakka mile?", "कम से कम कितने निकालूँ के एक जोड़ा पक्का मिले?",
                   "What's the fewest I must take to be sure of a pair?")], overlay=drawer(), dark=0.45)
EPS["riddle_moze"] = {"number": 313, "part": 1, "slug": "riddle_moze", "title": {"ur": "ANDHERE MEIN MOZE", "en": "SOCKS IN THE DARK"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5}, "answer_note": "3: with two colours, three socks always contain a pair.",
  "shots": [
    m0,
    question("small_bedroom", BUNTY, drawer(), "Kitne? Teen second!", "कितने? तीन सेकंड!", "How many? Three seconds!", main="KITNE MOZE? COMMENT KARO!", dark=0.45),
    {"set": "small_bedroom", "transition": "whoosh", "cast": BUNTY, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.5, "dark": 0.45,
     "overlay": drawer(pick_at=["@L0+0.5", "@L0+1.3", "@L1+0.4"]), "stamp": {"text": "SIRF 3!", "on": "bunty", "line": 2, "y": 1560},
     "lines": [ln("foxley", "Pehla kaala, doosra safed... chalo, bura qismat.", "पहला काला, दूसरा सफ़ेद... चलो, बुरी क़िस्मत।",
                  "First black, second white... bad luck.", sfx_before="reveal"),
               ln("foxley", "Lekin teesra kisi na kisi se milega hi! Sirf teen!", "लेकिन तीसरा किसी ना किसी से मिलेगा ही! सिर्फ़ तीन!",
                  "But the third must match one of them! Just three!"),
               ln("bunty", "Arey! Main to gyaarah bolne wala tha!", "अरे! मैं तो ग्यारह बोलने वाला था!", "Oh! I was about to say eleven!", pose="shocked")]},
    loop_shot(m0),
  ]}

# ===================================================================== 14. Raat Ka Pul
PUL = "raat_pul"
TIMES = {"bunty": 1, "zara": 2, "raju": 5, "jamil": 10}
NEAR_SLOTS = {"bunty": (150, 1380), "zara": (290, 1380), "raju": (430, 1380), "jamil": (570, 1380)}
FAR_SLOTS = {"bunty": (930, 718), "zara": (965, 718), "raju": (1000, 718), "jamil": (1035, 718)}
N_PT, F_PT = (335, 1050), (972, 716)
S_NEAR, S_N, S_F = 1.0, 0.75, 0.32
MINI_H = 230          # px height of a mini figure at scale 1


def mini(cid):
    r = rig(cid)
    cw, ch = r["canvas"]
    ih = MINI_H * ch / r["figure_height"] * r["height"] / 0.85
    iw = ih * cw / ch
    x, y = NEAR_SLOTS[cid]
    return (f'<div id="{{sid}}-m{cid}" style="position:absolute;left:{x - iw / 2:.0f}px;top:{y - ih:.0f}px;width:{iw:.0f}px;height:{ih:.0f}px;'
            f'transform-origin:50% 100%"><img src="cast/{cid}/pose_neutral.png" style="width:100%;height:100%"></div>'), (x, y)


LANTERN = ('<svg viewBox="0 0 40 60" width="100%" height="100%"><g stroke="#2B2B2B" stroke-width="3"><path d="M12 8 q8 -10 16 0" fill="none"/>'
           '<rect x="10" y="8" width="20" height="6" fill="#8A5A2B"/><path d="M8 14 h24 l-3 34 h-18z" fill="#FFE066"/><rect x="8" y="48" width="24" height="8" fill="#8A5A2B"/></g></svg>')


BANK_L, BANK_R, BANK_TOP = 70, 590, 1130
FIG_H = 210


def bridge(trips=(), counter=False):
    """two banks drawn as a board on the ledge: IS PAAR (left) and US PAAR (right); trips move the walkers
    and the lantern across. trips: (time expr, [walkers], to 'F'|'N', minutes so far after the trip)"""
    html = (f'<div style="position:absolute;left:40px;right:40px;top:{BANK_TOP - 60}px;height:380px;background:rgba(255,248,230,0.94);border:8px solid {INK};'
            f'border-radius:30px;box-shadow:0 12px 0 {INK}"></div>'
            f'<div style="position:absolute;left:532px;top:{BANK_TOP - 50}px;width:16px;height:360px;background:repeating-linear-gradient({INK} 0 18px,transparent 18px 30px)"></div>'
            + tag("IS PAAR", 290, BANK_TOP - 92, bg="#1F4E5F", fs=32, center=True)
            + tag("US PAAR", 810, BANK_TOP - 92, bg="#2E9E4F", fs=32, center=True))
    js, sfx = [], []
    slot_x = {c: 95 * i for i, c in enumerate(TIMES)}
    for c in TIMES:
        r = rig(c)
        cw, ch = r["canvas"]
        ih = FIG_H * ch / r["figure_height"] * r["height"]
        iw = ih * cw / ch
        x = BANK_L + slot_x[c] + 50
        html += (f'<div id="{{sid}}-m{c}" style="position:absolute;left:{x - iw / 2:.0f}px;top:{BANK_TOP + 255 - ih:.0f}px;width:{iw:.0f}px;height:{ih:.0f}px">'
                 f'<img src="cast/{c}/pose_neutral.png" style="width:100%;height:100%"></div>'
                 f'<div id="{{sid}}-t{c}" style="position:absolute;left:{x - 48}px;top:{BANK_TOP + 262}px;width:96px;text-align:center;font-weight:900;font-size:26px;color:{INK}">{TIMES[c]} MIN</div>')
    html += (f'<div id="{{sid}}-lamp" style="position:absolute;left:{BANK_L + 50 - 24}px;top:{BANK_TOP - 30}px;width:48px;height:72px">{LANTERN}</div>')
    if counter:
        vals = [0] + [t[3] for t in trips]
        html += (f'<div style="position:absolute;right:40px;top:600px;width:220px;height:120px;background:#C8342B;border:7px solid {INK};border-radius:22px;'
                 f'box-shadow:0 10px 0 {INK}"><div style="position:absolute;left:0;right:0;top:6px;text-align:center;color:#fff;font-weight:900;font-size:26px">MINUTE</div>')
        for v in sorted(set(vals)):
            html += (f'<div id="{{sid}}-c{v}" style="position:absolute;left:0;right:0;top:34px;text-align:center;color:#fff;font-weight:900;font-size:70px;'
                     f'opacity:{1 if v == 0 else 0}">{v}</div>')
        html += '</div>'
    side = {c: "N" for c in TIMES}
    shown = 0
    for t, walkers, to, total in trips:
        d = 0.9 + 0.12 * max(TIMES[w] for w in walkers)
        dx = BANK_R - BANK_L if to == "F" else 0
        for w in walkers:
            js.append(f'tl.to("#{{sid}}-m{w}", {{x: {dx}, duration: {d:.2f}, ease: "power1.inOut"}}, {t});')
            js.append(f'tl.to("#{{sid}}-t{w}", {{x: {dx}, duration: {d:.2f}, ease: "power1.inOut"}}, {t});')
            js.append(f'tl.to("#{{sid}}-m{w}", {{y: -14, duration: {d / 6:.2f}, yoyo: true, repeat: 5, ease: "sine.inOut"}}, {t});')
            side[w] = to
        lead = walkers[0]
        js.append(f'tl.to("#{{sid}}-lamp", {{x: {dx + slot_x[lead]}, duration: {d:.2f}, ease: "power1.inOut"}}, {t});')
        if counter:
            js.append(f'tl.set("#{{sid}}-c{shown}", {{opacity: 0}}, {t}+{d:.2f}); tl.set("#{{sid}}-c{total}", {{opacity: 1}}, {t}+{d:.2f});')
            js.append(f'tl.fromTo("#{{sid}}-c{total}", {{scale: 1.5}}, {{scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t}+{d:.2f});')
            sfx.append(["pop", f"{t}+{d:.2f}"])
            shown = total
        sfx.append(["whoosh", t])
    return ov(html, js, sfx)


FOUR = [{"id": c, "x": x} for c, x in zip(TIMES, (0.14, 0.38, 0.62, 0.86))]


def time_tags():
    h = ""
    for c, x in zip(TIMES, (0.14, 0.38, 0.62, 0.86)):
        hx, hy = head_top(c, x, 0.95)
        h += tag(f"{TIMES[c]} MIN", hx, hy - 70, center=True, bg="#1F4E5F", fs=32)
    return ov(h)


p0 = {"set": PUL, "cast": FOUR, "camera": STILL, "feet": 0.95, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1, "overlay": time_tags(),
      "hook": {"text": "17 MINUTE... EK LALTAIN... CHAAR LOG!", "y": 110, "dur": 99},
      "lines": [ln("foxley", "Raat ko yeh pul paar karna hai, aur laltain sirf ek hai!", "रात को ये पुल पार करना है, और लालटेन सिर्फ़ एक है!",
                   "They must cross this bridge at night, with only one lantern!")]}
RULES = {"title": "SHART", "rows": [["PUL PE", "SIRF 2 LOG"], ["LAALTAIN", "ZAROORI"], ["SAATH CHALEIN TO", "DHEERE WALE KI RAFTAAR"]], "y": 620, "rot": -2, "at": -1}
EPS["riddle_pul"] = {"number": 314, "part": 1, "slug": "riddle_pul", "title": {"ur": "RAAT KA PUL", "en": "THE NIGHT BRIDGE"},
  "handle": "@AskFoxley", "music": {"bpm": 98, "gain": 0.5},
  "answer_note": "Bunty+Zara (2), Bunty back (3), Raju+Jamil (13), Zara back (15), Bunty+Zara (17).",
  "shots": [
    p0,
    {"set": PUL, "transition": "whoosh", "cast": FOUR, "camera": STILL, "feet": 0.95, "caption_y": 230, "hold": 0.3, "card": RULES,
     "lines": [ln("foxley", "Pul pe ek saath sirf do log. Aur do log saath chalein, to dheere wale ki raftaar se.",
                  "पुल पे एक साथ सिर्फ़ दो लोग। और दो लोग साथ चलें, तो धीरे वाले की रफ़्तार से।",
                  "Only two on the bridge at once. And two walk at the slower one's speed.")]},
    {"set": PUL, "transition": "whoosh", "cast": FOUR, "camera": STILL, "feet": 0.95, "timer": 3, "timer_y": 1500, "caption_y": 1290,
     "sfx": [["riser", 0.0]], "hold": 0.6, "overlay": time_tags(),
     "cta": {"after_timer": True, "y": 160, "main": "KAISE? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."},
     "lines": [ln("foxley", "Kya sab satrah minute mein paar ho sakte hain?", "क्या सब सत्रह मिनट में पार हो सकते हैं?", "Can everyone cross in seventeen minutes?")]},
    {"set": PUL, "transition": "whoosh", "cast": [], "camera": STILL, "caption_y": 230, "hold": 0.8,
     "overlay": bridge(trips=[("@L0+0.3", ["bunty", "zara"], "F", 2), ("@L1+0.3", ["bunty"], "N", 3), ("@L2+0.3", ["raju", "jamil"], "F", 13),
                              ("@L3+0.3", ["zara"], "N", 15), ("@L4+0.3", ["bunty", "zara"], "F", 17)], counter=True),
     "stamp": {"text": "17 MINUTE!", "on": None, "line": 4, "y": 1560, "w": 700},
     "lines": [ln("foxley", "Bunty aur Zara saath: do minute.", "बंटी और ज़ारा साथ: दो मिनट।", "Bunty and Zara together: two minutes.", sfx_before="reveal"),
               ln("foxley", "Bunty laltain le kar wapas: teen.", "बंटी लालटेन ले कर वापस: तीन।", "Bunty brings the lantern back: three."),
               ln("foxley", "Ab Raju aur Chacha Jamil saath: terah!", "अब राजू और चाचा जमील साथ: तेरह!", "Now Raju and Chacha Jamil together: thirteen!"),
               ln("foxley", "Zara laltain le kar wapas: pandrah.", "ज़ारा लालटेन ले कर वापस: पंद्रह।", "Zara brings it back: fifteen."),
               ln("foxley", "Aur Bunty Zara phir saath... thik satrah minute!", "और बंटी ज़ारा फिर साथ... ठीक सत्रह मिनट!", "And Bunty and Zara again... exactly seventeen!")]},
    loop_shot(p0),
  ]}

# ===================================================================== 15. Kuen Ka Paani
KR = [{"id": "kareem", "x": 0.3, "face": "right"}, {"id": "raju", "x": 0.72}]
k0 = hook_shot("desert_village", KR, "KUAN BIK GAYA... PAANI NAHI!",
               ln("foxley", "Seth Kareem ne apna kuan Raju ko bech diya.", "सेठ करीम ने अपना कुआँ राजू को बेच दिया।", "Seth Kareem sold his well to Raju."))
EPS["riddle_kuan"] = {"number": 315, "part": 1, "slug": "riddle_kuan", "title": {"ur": "KUEN KA PAANI", "en": "THE WELL'S WATER"},
  "handle": "@AskFoxley", "music": {"bpm": 100, "gain": 0.5},
  "answer_note": "Raju: then take your water out of my well, or pay rent for keeping it there.",
  "shots": [
    k0,
    {"set": "desert_village", "transition": "whoosh", "cast": [{"id": "kareem", "x": 0.5}],
     "camera": {"from": {"focus": "kareem", "zoom": 1.25}, "to": {"focus": "kareem", "zoom": 1.35}}, "hold": 0.3,
     "lines": [ln("kareem", "Kuan tumhara, lekin paani mera! Paani ka kiraya do!", "कुआँ तुम्हारा, लेकिन पानी मेरा! पानी का किराया दो!",
                  "The well is yours, but the water is mine! Pay rent for the water!", after="signature_scheming")]},
    question("desert_village", KR, None, "Raju kya jawab de? Teen second!", "राजू क्या जवाब दे? तीन सेकंड!", "What should Raju say? Three seconds!",
             main="TUM KYA KEHTE? COMMENT KARO!"),
    {"set": "desert_village", "transition": "whoosh", "cast": KR, "camera": {"from": {"focus": "group", "zoom": 1.1}, "to": {"focus": "group", "zoom": 1.18}},
     "caption_y": 230, "hold": 0.5, "stamp": {"text": "KAMAAL!", "on": "raju", "line": 2, "y": 1560},
     "lines": [ln("raju", "Theek hai Seth ji! Apna paani mere kuen se nikaal lo...", "ठीक है सेठ जी! अपना पानी मेरे कुएँ से निकाल लो...",
                  "Fine, Seth ji! Take your water out of my well...", sfx_before="reveal"),
               ln("raju", "...warna mere kuen mein rakhne ka kiraya do!", "...वरना मेरे कुएँ में रखने का किराया दो!", "...or pay rent for keeping it in my well!"),
               ln("kareem", "Arey... yeh to main ne socha hi nahi!", "अरे... ये तो मैंने सोचा ही नहीं!", "Oh... I never thought of that!", pose="shocked")]},
    loop_shot(k0),
  ]}

# ===================================================================== 16. Teen Shikari
FISH = (f'<svg viewBox="0 0 120 60" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
        f'<path d="M10 30 q40 -34 80 0 q-40 34 -80 0z" fill="#64B5F6"/><path d="M88 30 l26 -18 v36z" fill="#64B5F6"/></g><circle cx="30" cy="26" r="4" fill="{INK}"/></svg>')
FAM = [("jamil", 0.2), ("raju", 0.5), ("bunty", 0.8)]


def fish_row(at=None):
    html = panel(PY - 10, 200, "3 MACHHLIYAN")
    js = []
    for i in range(3):
        html += f'<div id="{{sid}}-f{i}" style="position:absolute;left:{170 + i * 270}px;top:{PY + 50}px;width:200px;height:100px">{FISH}</div>'
    return html, js


def shikari_overlay(roles_at=None, fish_at=None):
    html, js = fish_row()
    sfx = []
    if roles_at:
        roles = {"jamil": [("DADA", "#1F4E5F")], "raju": [("BAAP", "#2E9E4F"), ("BETA", "#E8762B")], "bunty": [("BETA", "#E8762B")]}
        for c, x in FAM:
            hx, hy = head_top(c, x, 0.93)
            for j, (txt, col) in enumerate(roles[c]):
                idx = f"r{c}{j}"
                html += tag(txt, hx, hy - 80 - 62 * j, idx, bg=col, fs=34, center=True)
                js.append(pop(idx, roles_at[c][j]))
                sfx.append(["pop", roles_at[c][j]])
    if fish_at:
        for i, (c, x) in enumerate(FAM):
            hx, hy = head_top(c, x, 0.93)
            fig_h = H * BASE_H * rig(c)["height"]
            tx, ty = hx - 40, hy + 0.55 * fig_h - 50
            js.append(f'tl.to("#{{sid}}-f{i}", {{x: {tx - (170 + i * 270)}, y: {ty - (PY + 50)}, scale: 0.7, duration: 0.6, ease: "power2.inOut"}}, {fish_at}+{0.2 * i:.1f});')
        sfx.append(["whoosh", fish_at])
    return ov(html, js, sfx)


FAMC = [{"id": c, "x": x} for c, x in FAM]
s0 = hook_shot("river_ghat", FAMC, "DO BAAP, DO BETE... PHIR BHI TEEN MACHHLIYAN!",
               [ln("foxley", "Do baap aur do bete machhli pakarne gaye.", "दो बाप और दो बेटे मछली पकड़ने गए।", "Two fathers and two sons went fishing."),
                ln("foxley", "Teen machhliyan pakri, aur sab ko ek-ek mili. Kaise?", "तीन मछलियाँ पकड़ीं, और सब को एक-एक मिली। कैसे?",
                   "They caught three fish, and each got one. How?")], overlay=shikari_overlay())
EPS["riddle_shikari"] = {"number": 316, "part": 1, "slug": "riddle_shikari", "title": {"ur": "TEEN SHIKARI", "en": "THREE FISHERMEN"},
  "handle": "@AskFoxley", "music": {"bpm": 102, "gain": 0.5},
  "answer_note": "Only three people: grandfather Jamil, his son Raju, and Raju's son Bunty.",
  "shots": [
    s0,
    question("river_ghat", FAMC, shikari_overlay(), "Kaise? Teen second!", "कैसे? तीन सेकंड!", "How? Three seconds!", main="KAISE? COMMENT KARO!"),
    {"set": "river_ghat", "transition": "whoosh", "cast": FAMC, "camera": STILL, "feet": 0.93, "caption_y": 230, "hold": 0.5,
     "overlay": shikari_overlay(roles_at={"jamil": ["@L0+0.6"], "raju": ["@L1+0.3", "@L1+1.4"], "bunty": ["@L0+1.4"]}, fish_at="@L2+0.3"),
     "stamp": {"text": "KAMAAL!", "on": "bunty", "line": 2, "y": 1600},
     "lines": [ln("foxley", "Woh sirf teen the! Dada, baap aur beta.", "वो सिर्फ़ तीन थे! दादा, बाप और बेटा।", "There were only three! Grandfather, father and son.",
                  sfx_before="reveal"),
               ln("foxley", "Raju, Jamil ka beta bhi hai... aur Bunty ka baap bhi!", "राजू, जमील का बेटा भी है... और बंटी का बाप भी!",
                  "Raju is Jamil's son... and Bunty's father too!"),
               ln("bunty", "Teen log, teen machhliyan!", "तीन लोग, तीन मछलियाँ!", "Three people, three fish!")]},
    loop_shot(s0),
  ]}

# ===================================================================== 17. Chhe Glass
GX = [95 + i * 150 for i in range(6)]
GY = PY + 60
GW, GH = 120, 200


def glasses(pour_at=None):
    html = panel(PY - 10, 360, "6 GLASS")
    js, sfx = [], []
    for i, x in enumerate(GX):
        full = i < 3
        html += (f'<div id="{{sid}}-g{i}" style="position:absolute;left:{x}px;top:{GY}px;width:{GW}px;height:{GH}px;transform-origin:50% 50%">'
                 f'<div style="position:absolute;inset:0;border:7px solid {INK};border-top:none;border-radius:0 0 22px 22px;background:rgba(230,245,255,0.6);overflow:hidden">'
                 f'<div id="{{sid}}-l{i}" style="position:absolute;left:0;right:0;bottom:0;height:{150 if full else 0}px;background:#FFF3C4;border-top:5px solid #F2D27A"></div></div></div>'
                 + badge(i + 1, x + 30, GY + GH + 16, 56, 34))
    if pour_at:
        dx = GX[4] - GX[1]
        js += [f'tl.to("#{{sid}}-g1", {{y: -120, duration: 0.4, ease: "power2.out"}}, {pour_at});',
               f'tl.to("#{{sid}}-g1", {{x: {dx - 70}, duration: 0.6, ease: "power2.inOut"}}, {pour_at}+0.4);',
               f'tl.to("#{{sid}}-g1", {{rotation: 70, duration: 0.4}}, {pour_at}+1.0);',
               f'tl.to("#{{sid}}-l1", {{height: 0, duration: 0.8}}, {pour_at}+1.3);',
               f'tl.to("#{{sid}}-l4", {{height: 150, duration: 0.8}}, {pour_at}+1.3);',
               f'tl.to("#{{sid}}-g1", {{rotation: 0, duration: 0.3}}, {pour_at}+2.2);',
               f'tl.to("#{{sid}}-g1", {{x: 0, y: 0, duration: 0.6, ease: "power2.inOut"}}, {pour_at}+2.5);']
        sfx += [["whoosh", pour_at], ["pop", f"{pour_at}+1.3"]]
    return ov(html, js, sfx)


def glasses_done(at):
    o = glasses()
    o["html"] = o["html"].replace('id="{sid}-l1" style="position:absolute;left:0;right:0;bottom:0;height:150px',
                                  'id="{sid}-l1" style="position:absolute;left:0;right:0;bottom:0;height:0px')
    o["html"] = o["html"].replace('id="{sid}-l4" style="position:absolute;left:0;right:0;bottom:0;height:0px',
                                  'id="{sid}-l4" style="position:absolute;left:0;right:0;bottom:0;height:150px')
    labels = ["BHARA", "KHAALI", "BHARA", "KHAALI", "BHARA", "KHAALI"]
    for i, x in enumerate(GX):
        o["html"] += tag(labels[i], x + GW / 2, GY - 64, f"t{i}", bg="#2E9E4F" if i % 2 == 0 else "#1F4E5F", fs=24, center=True)
        o["js"].append(pop(f"t{i}", f"{at}+{0.25 * i:.2f}"))
    o["sfx"].append(["reveal", at])
    return o


ZARA = [{"id": "zara", "x": 0.5}]
g0 = hook_shot("kitchen", ZARA, "SIRF EK GLASS CHHOO SAKTE HO!",
               [ln("foxley", "Pehle teen glass mein lassi, baaki teen khaali.", "पहले तीन ग्लास में लस्सी, बाक़ी तीन ख़ाली।",
                   "The first three glasses have lassi, the other three are empty."),
                ln("foxley", "Sirf ek glass chhoo kar, inhein bhara-khaali-bhara karo!", "सिर्फ़ एक ग्लास छू कर, इन्हें भरा-ख़ाली-भरा करो!",
                   "Touch just one glass and make them full-empty-full!")], overlay=glasses())
EPS["riddle_glass"] = {"number": 317, "part": 1, "slug": "riddle_glass", "title": {"ur": "CHHE GLASS", "en": "SIX GLASSES"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5}, "answer_note": "Pick up glass 2, pour it into glass 5, put it back.",
  "shots": [
    g0,
    question("kitchen", ZARA, glasses(), "Kaunsa glass? Teen second!", "कौनसा ग्लास? तीन सेकंड!", "Which glass? Three seconds!",
             main="KAUNSA GLASS? COMMENT KARO!"),
    {"set": "kitchen", "transition": "whoosh", "cast": ZARA, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.3,
     "overlay": glasses(pour_at="@L0+0.3"),
     "lines": [ln("foxley", "Doosra glass uthao... aur paanchwe mein daal do!", "दूसरा ग्लास उठाओ... और पाँचवें में डाल दो!",
                  "Pick up glass two... and pour it into glass five!", sfx_before="reveal")]},
    {"set": "kitchen", "cast": ZARA, "camera": cam(), "feet": 0.93, "caption_y": 230, "hold": 0.5, "overlay": glasses_done("@L0+0.2"),
     "stamp": {"text": "KAMAAL!", "on": "zara", "line": 1, "y": 1560},
     "lines": [ln("foxley", "Ab dekho: bhara, khaali, bhara, khaali!", "अब देखो: भरा, ख़ाली, भरा, ख़ाली!", "Now look: full, empty, full, empty!"),
               ln("zara", "Arey waah! Itna aasaan!", "अरे वाह! इतना आसान!", "Oh wow! That easy!")]},
    loop_shot(g0),
  ]}

for name, ep in EPS.items():
    json.dump(ep, open(os.path.join(ROOT, "episodes", f"{name}.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote episodes/%s.json" % name)
