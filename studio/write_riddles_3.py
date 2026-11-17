"""Writes riddles 1-5 of planning/NEW_RIDDLES.md (2026-11-17), all props drawn in code:

  episodes/riddle_lathi.json     Jaadui Lathi        wit + whodunit   kareem_shop
  episodes/riddle_icecream.json  Pighalti Ice Cream  whodunit A       town_park
  episodes/riddle_sikka.json     Halka Sikka         logic            kareem_shop
  episodes/riddle_kichad.json    Kichad Ke Nishaan   whodunit A       garden
  episodes/riddle_maachis.json   Ek Maachis          quick paheli     kitchen (night)

    python3 studio/write_riddles_3.py
Single Reels: hook on the first frame, answer included, the last shot repeats the first so it loops.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2B2B2B"
PY = 640          # top of the prop panel (below the captions, above the characters' heads)


def ln(who, cap, say, en, **k):
    return {"who": who, "caption": cap, "say": say, "en": en, **k}


def panel(h=360, title=None):
    t = (f'<div style="position:absolute;left:0;right:0;top:-34px;text-align:center"><span style="background:#1F4E5F;color:#fff;font-weight:900;'
         f'font-size:36px;padding:4px 24px;border:6px solid {INK};border-radius:18px">{title}</span></div>') if title else ""
    return (f'<div style="position:absolute;left:40px;right:40px;top:{PY}px;height:{h}px;background:rgba(255,248,230,0.94);'
            f'border:8px solid {INK};border-radius:30px;box-shadow:0 12px 0 {INK}">{t}</div>')


def numbadge(n, x, y, size=70, fs=44):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;border-radius:50%;background:#F2B134;'
            f'border:6px solid {INK};display:flex;align-items:center;justify-content:center;font-weight:900;font-size:{fs}px;color:{INK}">{n}</div>')


def tag(text, x, y, bg="#C8342B", fs=34, idx=None):
    i = f' id="{{sid}}-{idx}"' if idx else ""
    return (f'<div{i} style="position:absolute;left:{x}px;top:{y}px;background:{bg};color:#fff;font-weight:900;font-size:{fs}px;white-space:nowrap;'
            f'padding:4px 18px;border:5px solid {INK};border-radius:16px;{"opacity:0;" if idx else ""}">{text}</div>')


def pop(idx, t, sfx="pop"):
    return ([f'tl.fromTo("#{{sid}}-{idx}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t});'],
            [[sfx, t]] if sfx else [])


def ov(html, js=(), sfx=()):
    return {"html": html, "js": list(js), "sfx": [list(s) for s in sfx]}


def lineup_shot(set_, ids, **k):
    return {"set": set_, "cast": [{"id": c, "x": x} for c, x in zip(ids, (0.2, 0.5, 0.8))], "lineup": ids, "lineup_at": 0,
            "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}}, **k}


def close(set_, cid, num=None, pose=None, fixed=False, **k):
    c = {"id": cid, "x": 0.5}
    if num: c["num"] = num
    if pose: c["pose"] = pose
    cam = {"from": {"focus": cid, "zoom": 1.25}, "to": {"focus": cid, "zoom": 1.25 if fixed else 1.4}}
    return {"set": set_, "transition": "whoosh", "cast": [c], "camera": cam, "hold": 0.2, **k}


def wide(set_, cid, pose=None, **k):
    """answer shot with a prop panel on screen: no zoom, so the panel never covers the face"""
    c = {"id": cid, "x": 0.5, **({"pose": pose} if pose else {})}
    return {"set": set_, "transition": "whoosh", "cast": [c], "feet": 0.93,
            "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.03}}, **k}


def question(set_, ids, overlay=None, text="Kaun jhoota hai? Teen second!", say="कौन झूठा है? तीन सेकंड!", en="Who's lying? Three seconds!",
             main="1, 2 YA 3? COMMENT KARO!", **k):
    sh = lineup_shot(set_, ids, transition="whoosh", sfx=[["riser", 0.0]], timer=3, timer_y=1500, caption_y=1290, feet=0.93,
                     cta={"after_timer": True, "y": 160, "main": main, "sub": "Jawab abhi aa raha hai..."}, hold=0.6,
                     lines=[ln("foxley", text, say, en)], **k)
    if overlay: sh["overlay"] = overlay
    return sh


EPS = {}

# ===================================================================== 1. Jaadui Lathi
def sticks(short=False, mark_at=None):
    base = PY + 320
    html = panel(360, "LATHIYAN")
    js, sfx = [], []
    for k, x in enumerate((230, 520, 810)):
        h = 250 if not (short and k == 1) else 180
        html += (f'<div style="position:absolute;left:{x}px;top:{base - h}px;width:40px;height:{h}px;background:linear-gradient(90deg,#8A5A2B,#B97A3C,#8A5A2B);'
                 f'border:5px solid {INK};border-radius:14px"></div>')
        html += numbadge(k + 1, x - 15, base + 6, 66, 40)
    html += f'<div style="position:absolute;left:150px;right:150px;top:{base - 250 - 3}px;border-top:5px dashed #C8342B;opacity:{1 if short else 0}"></div>'
    if mark_at:
        html += (f'<div id="{{sid}}-gap" style="position:absolute;left:575px;top:{base - 236}px;opacity:0;font-weight:900;color:#C8342B;font-size:38px;white-space:nowrap">'
                 f'&larr; 1 INCH KAATI!</div>')
        j, s = pop("gap", mark_at); js += j; sfx += s
    return ov(html, js, sfx)


SUSP1 = ["raju", "faisal", "sherkhan"]
EPS["riddle_lathi"] = {"number": 301, "part": 1, "slug": "riddle_lathi", "title": {"ur": "JAADUI LATHI", "en": "THE MAGIC STICK"},
  "handle": "@AskFoxley", "music": {"bpm": 102, "gain": 0.5},
  "answer_note": "Faisal (2) cut his stick by an inch, afraid it would grow. The stick was never magic.",
  "shots": [
    {"set": "kareem_shop", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.05}, "to": {"focus": [0.5, 0.62], "zoom": 1.1}},
     "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1, "hook": {"text": "CHOR NE KHUD KO PAKARWA DIYA... KAISE?", "y": 110, "dur": 99},
     "lines": [ln("kareem", "Meri dukaan se sone ke sikke chori ho gaye!", "मेरी दुकान से सोने के सिक्के चोरी हो गए!", "Gold coins were stolen from my shop!", after="shocked")]},
    lineup_shot("kareem_shop", SUSP1, transition="whoosh", caption_y=230, hold=0.2, feet=0.93, overlay=sticks(),
                lines=[ln("foxley", "Teen log dukaan mein the. Chacha Jamil ne sab ko ek jaisi lathi di.",
                          "तीन लोग दुकान में थे। चाचा जमील ने सब को एक जैसी लाठी दी।",
                          "Three people were in the shop. Chacha Jamil gave each the same stick.")]),
    close("kareem_shop", "jamil", hold=0.3,
          lines=[ln("jamil", "Chor ki lathi raat bhar mein ek inch lambi ho jayegi!", "चोर की लाठी रात भर में एक इंच लंबी हो जाएगी!",
                    "The thief's stick will grow one inch overnight!", after="signature_cane_shake")]),
    lineup_shot("kareem_shop", SUSP1, transition="whoosh", dark=0.72, caption_y=1290, hold=0.2, hook={"text": "RAAT GUZAR GAYI...", "y": 660, "dur": 99},
                lines=[ln("foxley", "Agli subah...", "अगली सुबह...", "The next morning...")]),
    question("kareem_shop", SUSP1, overlay=sticks(short=True), text="Chor kaun hai? Teen second!", say="चोर कौन है? तीन सेकंड!", en="Who is the thief? Three seconds!"),
    wide("kareem_shop", "faisal", pose="nervous", caption_y=230, hold=0.5,
          overlay=sticks(short=True, mark_at="@L1+0.3"),
          stamp={"text": {"ur": "MUJRIM!", "en": "GUILTY!"}, "on": "faisal", "line": 2, "y": 1560},
          lines=[ln("foxley", "Lathi jaadui thi hi nahi!", "लाठी जादुई थी ही नहीं!", "The stick was never magic!", sfx_before="reveal"),
                 ln("foxley", "Chor ne dar ke maare apni lathi ek inch kaat di!", "चोर ने डर के मारे अपनी लाठी एक इंच काट दी!",
                    "The thief got scared and cut his stick by an inch!"),
                 ln("faisal", "Main ne socha lambi ho gayi to pakra jaunga!", "मैंने सोचा लंबी हो गई तो पकड़ा जाऊँगा!",
                    "I thought if it grew, I'd be caught!", pose="guilty")]),
    {"set": "kareem_shop", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.05}, "to": {"focus": [0.5, 0.62], "zoom": 1.05}}, "hold": 0.6},
  ]}

# ===================================================================== 2. Pighalti Ice Cream
THERMO = ('<div style="position:absolute;right:50px;top:{y}px;width:250px;height:150px;background:#FFF5DC;border:7px solid #2B2B2B;border-radius:22px;'
          'box-shadow:0 8px 0 #2B2B2B;display:flex;align-items:center;justify-content:center;gap:8px">'
          '<svg viewBox="0 0 60 60" width="62" height="62"><circle cx="30" cy="30" r="13" fill="#F2B134" stroke="#2B2B2B" stroke-width="4"/>'
          + "".join(f'<path d="M{30 + 19 * math.cos(a / 8 * 6.283):.1f} {30 + 19 * math.sin(a / 8 * 6.283):.1f} L{30 + 27 * math.cos(a / 8 * 6.283):.1f} {30 + 27 * math.sin(a / 8 * 6.283):.1f}" stroke="#E8762B" stroke-width="5" stroke-linecap="round"/>' for a in range(8))
          + '</svg><span style="font-weight:900;font-size:64px;color:#C8342B">40°C</span></div>')


def cone(x, y, w=150):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w * 1.5:.0f}px"><svg viewBox="0 0 100 150" width="100%" height="100%">'
            f'<g stroke="{INK}" stroke-width="4" stroke-linejoin="round">'
            f'<path d="M22 62 L50 146 L78 62 Z" fill="#D9A15A"/><path d="M32 70 L60 120 M45 66 L68 100 M60 66 L42 120 M74 70 L55 108" stroke="#A86E2C" stroke-width="3" fill="none"/>'
            f'<circle cx="50" cy="56" r="27" fill="#F8C8D8"/><circle cx="38" cy="36" r="20" fill="#FFF5E6"/><circle cx="62" cy="36" r="20" fill="#8B5A3C"/>'
            f'<circle cx="52" cy="14" r="8" fill="#C8342B"/></g>'
            f'<path d="M44 46 q6 4 12 0" stroke="#fff" stroke-width="3" fill="none"/></svg></div>')


def park_overlay(y_thermo=640, with_cone=None, mark_at=None):
    html = THERMO.replace("{y}", str(y_thermo))
    js, sfx = [], []
    if with_cone:
        html += cone(*with_cone)
        if mark_at:
            x, y, w = with_cone
            html += (f'<div id="{{sid}}-ring" style="position:absolute;left:{x - 40}px;top:{y - 30}px;width:{w + 80}px;height:{w * 1.5 + 60:.0f}px;'
                     f'border:10px solid #C8342B;border-radius:50%;opacity:0"></div>')
            html += tag("BILKUL JAMI HUI!", x - 140, y + w * 1.5 + 40, idx="frozen")
            j, s = pop("ring", mark_at); js += j; sfx += s
            j, s = pop("frozen", f"{mark_at}+0.5", None); js += j
    return ov(html, js, sfx)


SUSP2 = ["jamil", "faisal", "zara"]
CONE_AT = (640, 1140, 120)     # set by eye on a snapshot (zara's free hand at fixed zoom 1.25)
EPS["riddle_icecream"] = {"number": 302, "part": 1, "slug": "riddle_icecream", "title": {"ur": "PIGHALTI ICE CREAM", "en": "THE MELTING ICE CREAM"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5},
  "answer_note": "Zara (3): in 40-degree heat an ice cream melts in minutes, yet hers is still frozen, so she only just bought it.",
  "shots": [
    {"set": "town_park", "cast": [{"id": "ayesha", "x": 0.42}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.05}, "to": {"focus": [0.5, 0.62], "zoom": 1.1}},
     "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1, "hook": {"text": "40 DEGREE GARMI... AUR EK JHOOT!", "y": 110, "dur": 99},
     "overlay": park_overlay(400),
     "lines": [ln("ayesha", "Park se meri cycle chori ho gayi!", "पार्क से मेरी साइकिल चोरी हो गई!", "My bicycle was stolen from the park!", after="shocked")]},
    close("town_park", "jamil", num=1, overlay=park_overlay(400),
          lines=[ln("jamil", "Main to bench pe akhbaar padh raha tha.", "मैं तो बेंच पे अख़बार पढ़ रहा था।", "I was reading the newspaper on the bench.")]),
    close("town_park", "faisal", num=2, overlay=park_overlay(400),
          lines=[ln("faisal", "Main saamne dhaabe pe khana kha raha tha.", "मैं सामने ढाबे पे खाना खा रहा था।", "I was eating at the dhaba across the road.")]),
    close("town_park", "zara", num=3, fixed=True, hold=0.6, overlay=park_overlay(400, with_cone=CONE_AT),
          lines=[ln("zara", "Main ek ghante se yahan baith ke ice cream kha rahi hoon!", "मैं एक घंटे से यहाँ बैठ के आइसक्रीम खा रही हूँ!",
                    "I've been sitting here eating ice cream for an hour!")]),
    question("town_park", SUSP2, overlay=park_overlay(400)),
    close("town_park", "zara", fixed=True, caption_y=230, hold=0.5, overlay=park_overlay(640, with_cone=CONE_AT, mark_at="@L0+0.3"),
          verdicts=[{"on": "zara", "ok": False, "line": 1, "at": 0.1, "lift": 60}],
          stamp={"text": {"ur": "MUJRIM!", "en": "GUILTY!"}, "on": "zara", "line": 2, "y": 1560},
          lines=[ln("foxley", "Chaalees degree mein ice cream minton mein pighal jaati hai!", "चालीस डिग्री में आइसक्रीम मिनटों में पिघल जाती है!",
                    "At 40 degrees, ice cream melts in minutes!", sfx_before="reveal"),
                 ln("foxley", "Yeh bilkul jami hui hai. Zara abhi aayi hai!", "ये बिल्कुल जमी हुई है। ज़ारा अभी आई है!",
                    "This one is still frozen. Zara just got here!"),
                 ln("zara", "Achha achha... cycle bhi main ne hi li thi.", "अच्छा अच्छा... साइकिल भी मैंने ही ली थी।",
                    "Okay, okay... I took the bicycle too.", pose="guilty")]),
    {"set": "town_park", "cast": [{"id": "ayesha", "x": 0.42}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.05}, "to": {"focus": [0.5, 0.62], "zoom": 1.05}},
     "overlay": park_overlay(400), "hold": 0.6},
  ]}

# ===================================================================== 3. Halka Sikka
COIN = (f'<svg viewBox="0 0 60 60" width="100%" height="100%"><circle cx="30" cy="30" r="26" fill="#F2B134" stroke="{INK}" stroke-width="5"/>'
        f'<circle cx="30" cy="30" r="17" fill="none" stroke="#C98A1C" stroke-width="4"/><path d="M24 22 h12 M24 30 h12 M24 38 h12" stroke="#C98A1C" stroke-width="3"/></svg>')
FAKE_COIN = COIN.replace("#F2B134", "#E9C46A")


def coin(cid, x, y, fake=False, size=62):
    return f'<div id="{{sid}}-{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px">{FAKE_COIN if fake else COIN}</div>'


def scale(groups, tilt_at=None, tilt=-12, fake_mark=None):
    """balance scale; groups = (left coins, right coins, aside coins) as counts; the right pan holds the fake (lighter)"""
    cx, py = 540, PY + 70           # pivot
    L = 280
    html = panel(380)
    html += (f'<div style="position:absolute;left:{cx - 12}px;top:{py}px;width:24px;height:250px;background:#8A5A2B;border:5px solid {INK};border-radius:8px"></div>'
             f'<div style="position:absolute;left:{cx - 110}px;top:{py + 240}px;width:220px;height:34px;background:#8A5A2B;border:5px solid {INK};border-radius:12px"></div>')
    html += (f'<div id="{{sid}}-beam" style="position:absolute;left:{cx - L}px;top:{py - 10}px;width:{2 * L}px;height:22px;background:#C98A1C;border:5px solid {INK};'
             f'border-radius:12px;transform-origin:50% 50%"></div><div style="position:absolute;left:{cx - 18}px;top:{py - 16}px;width:36px;height:36px;border-radius:50%;'
             f'background:{INK}"></div>')
    def pan(side, n, fake_idx=None):
        x = cx - L if side == "l" else cx + L
        coins = "".join(coin(f"{side}c{i}", 30 + (i % 3) * 52 - (26 if n == 1 else 0) + (52 if n == 1 else 0), 30 - (i // 3) * 50, fake=(i == fake_idx)) for i in range(n))
        return (f'<div id="{{sid}}-pan{side}" style="position:absolute;left:{x - 110}px;top:{py}px;width:220px;height:170px">'
                f'<svg viewBox="0 0 220 170" width="100%" height="100%" style="position:absolute;left:0;top:0"><path d="M110 0 L20 120 M110 0 L200 120" stroke="{INK}" stroke-width="4"/>'
                f'<path d="M10 118 h200 q-10 40 -100 40 q-90 0 -100 -40z" fill="#C98A1C" stroke="{INK}" stroke-width="5"/></svg>'
                f'<div style="position:absolute;left:0;top:58px;width:220px;height:62px">{coins}</div></div>')
    nl, nr, na = groups
    html += pan("l", nl) + pan("r", nr, fake_idx=(1 if nr == 3 else 0))
    html += "".join(coin(f"a{i}", 860 + (i % 2) * 64 - (0 if na > 1 else -30), PY + 250 - (i // 2) * 58) for i in range(na))
    js, sfx = [], []
    if tilt_at:
        d = L * math.sin(math.radians(abs(tilt)))
        js += [f'tl.to("#{{sid}}-beam", {{rotation: {tilt}, duration: 0.8, ease: "elastic.out(1, 0.5)"}}, {tilt_at});',
               f'tl.to("#{{sid}}-panl", {{y: {d:.0f}, duration: 0.8, ease: "elastic.out(1, 0.5)"}}, {tilt_at});',
               f'tl.to("#{{sid}}-panr", {{y: {-d:.0f}, duration: 0.8, ease: "elastic.out(1, 0.5)"}}, {tilt_at});']
        sfx.append(["whoosh", tilt_at])
        html += tag("HALKA!" if nr == 3 else "NAQLI!", cx + L - 80, py - 110, idx="light")
        j, s = pop("light", f"{tilt_at}+0.6"); js += j; sfx += s
    return ov(html, js, sfx)


def nine_coins(group_at=None):
    html = panel(300, "9 SIKKE")
    js = []
    for i in range(9):
        x, y = 95 + i * 100, PY + 110
        html += coin(f"n{i}", x, y, size=80)
        if group_at:
            gx = 95 + (i // 3) * 330 + (i % 3) * 90
            js.append(f'tl.to("#{{sid}}-n{i}", {{x: {gx - x}, duration: 0.5, ease: "power2.inOut"}}, {group_at});')
    if group_at:
        for g in range(3):
            html += tag(f"{g + 1}", 160 + g * 330, PY + 210, bg="#1F4E5F", idx=f"g{g}")
            js += pop(f"g{g}", f"{group_at}+0.5", None)[0]
    return ov(html, js, [["whoosh", group_at]] if group_at else [])


EPS["riddle_sikka"] = {"number": 303, "part": 1, "slug": "riddle_sikka", "title": {"ur": "HALKA SIKKA", "en": "THE LIGHT COIN"},
  "handle": "@AskFoxley", "music": {"bpm": 100, "gain": 0.5},
  "answer_note": "Split 3-3-3; weigh two groups (the lighter pan, or the third group if they balance, has the fake); then weigh 1 against 1 of those 3.",
  "shots": [
    {"set": "kareem_shop", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}},
     "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1, "hook": {"text": "9 SIKKE, 1 NAQLI... SIRF 2 BAAR TARAAZU!", "y": 110, "dur": 99},
     "overlay": nine_coins(),
     "lines": [ln("kareem", "Inn nau sikkon mein ek naqli hai. Woh thoda halka hai.", "इन नौ सिक्कों में एक नक़ली है। वो थोड़ा हल्का है।",
                  "One of these nine coins is fake. It's a little lighter.")]},
    {"set": "kareem_shop", "transition": "whoosh", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}},
     "overlay": scale((0, 0, 0)), "timer": 3, "timer_y": 1500, "caption_y": 1290, "sfx": [["riser", 0.0]],
     "cta": {"after_timer": True, "y": 160, "main": "KAISE DHOONDOGE? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."}, "hold": 0.6,
     "lines": [ln("foxley", "Taraazu sirf do baar! Naqli sikka kaise dhoondoge?", "तराज़ू सिर्फ़ दो बार! नक़ली सिक्का कैसे ढूँढोगे?",
                  "The scale only twice! How do you find the fake?")]},
    {"set": "kareem_shop", "transition": "whoosh", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.02}},
     "overlay": nine_coins(group_at="@L0+0.4"), "caption_y": 230, "hold": 0.2,
     "lines": [ln("foxley", "Pehle teen-teen ke teen hisse banao.", "पहले तीन-तीन के तीन हिस्से बनाओ।", "First, make three groups of three.", sfx_before="reveal")]},
    {"set": "kareem_shop", "transition": "whoosh", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.02}},
     "overlay": scale((3, 3, 3), tilt_at="@L0+0.6"), "caption_y": 230, "hold": 0.3,
     "lines": [ln("foxley", "Do hisse taraazu pe. Jo halka, naqli usi mein. Barabar ho to teesre mein.",
                  "दो हिस्से तराज़ू पे। जो हल्का, नक़ली उसी में। बराबर हो तो तीसरे में।",
                  "Two groups on the scale. The lighter one has the fake. If equal, it's in the third.")]},
    {"set": "kareem_shop", "transition": "whoosh", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.02}},
     "overlay": scale((1, 1, 1), tilt_at="@L0+0.6"), "caption_y": 230, "hold": 0.4,
     "stamp": {"text": "KAMAAL!", "on": "kareem", "line": 1, "y": 1560},
     "lines": [ln("foxley", "Ab unn teen mein se ek-ek taraazu pe. Wohi tareeqa!", "अब उन तीन में से एक-एक तराज़ू पे। वही तरीक़ा!",
                  "Now one against one from those three. Same trick!"),
               ln("kareem", "Waah! Sirf do baar mein pakar liya!", "वाह! सिर्फ़ दो बार में पकड़ लिया!", "Wow! Caught it in just two goes!")]},
    {"set": "kareem_shop", "cast": [{"id": "kareem", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.0}},
     "overlay": nine_coins(), "hold": 0.6},
  ]}

# ===================================================================== 4. Kichad Ke Nishaan
def footprints(mark_at=None):
    html = panel(360, "KICHAD KE NISHAAN")
    html = html.replace("rgba(255,248,230,0.94)", "#D8B98A")
    js, sfx = [], []
    for k in range(8):
        x, y = 110 + k * 110, PY + 250 - k * 22 + (28 if k % 2 else 0)
        html += (f'<div style="position:absolute;left:{x}px;top:{y}px;width:52px;height:76px;transform:rotate(80deg)">'
                 f'<svg viewBox="0 0 50 76" width="100%" height="100%"><ellipse cx="25" cy="44" rx="17" ry="28" fill="#5A3A1E"/>'
                 + "".join(f'<circle cx="{10 + i * 8}" cy="{10 - abs(2 - i) * 2}" r="4.5" fill="#5A3A1E"/>' for i in range(5)) + '</svg></div>')
        if k % 2 == 1:
            html += f'<div style="position:absolute;left:{x + 18}px;top:{y + 80}px;width:20px;height:20px;border-radius:50%;background:#3A2410"></div>'
            if mark_at:
                html += (f'<div id="{{sid}}-r{k}" style="position:absolute;left:{x - 2}px;top:{y + 60}px;width:60px;height:60px;border:7px solid #C8342B;'
                         f'border-radius:50%;opacity:0"></div>')
                j, s = pop(f"r{k}", f"{mark_at}+{0.2 * (k // 2):.1f}", "pop" if k == 1 else None); js += j; sfx += s
    if mark_at:
        html += tag("CHHADI KE NISHAAN!", 330, PY + 40, idx="lbl")
        j, s = pop("lbl", f"{mark_at}+1.0", None); js += j
    return ov(html, js, sfx)


SUSP4 = ["rafiq", "jamil", "raju"]
EPS["riddle_kichad"] = {"number": 304, "part": 1, "slug": "riddle_kichad", "title": {"ur": "KICHAD KE NISHAAN", "en": "FOOTPRINTS IN THE MUD"},
  "handle": "@AskFoxley", "music": {"bpm": 102, "gain": 0.5},
  "answer_note": "Chacha Jamil (2): a round dot beside every second footprint is the mark of his walking stick.",
  "shots": [
    {"set": "garden", "cast": [{"id": "nusrat", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}},
     "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1, "hook": {"text": "KICHAD NE CHOR KA RAAZ KHOL DIYA!", "y": 110, "dur": 99},
     "overlay": footprints(),
     "lines": [ln("nusrat", "Barish ke baad mera trophy gayab ho gaya!", "बारिश के बाद मेरी ट्रॉफ़ी ग़ायब हो गई!", "My trophy vanished after the rain!", after="shocked")]},
    close("garden", "rafiq", num=1, lines=[ln("rafiq", "Main to kitchen mein khana bana raha tha.", "मैं तो किचन में खाना बना रहा था।", "I was cooking in the kitchen.")]),
    close("garden", "jamil", num=2, lines=[ln("jamil", "Main subah se veranda mein apni kursi pe baitha hoon.", "मैं सुबह से वरांडा में अपनी कुर्सी पे बैठा हूँ।",
                                             "I've been sitting in my chair on the veranda all morning.")]),
    close("garden", "raju", num=3, lines=[ln("raju", "Main gate pe rang kar raha tha.", "मैं गेट पे रंग कर रहा था।", "I was painting the gate.")]),
    question("garden", SUSP4, overlay=footprints(), text="Nishaan ghaur se dekho! Kaun jhoota?", say="निशान ग़ौर से देखो! कौन झूठा?",
             en="Look closely at the prints! Who's lying?"),
    wide("garden", "jamil", pose="nervous", caption_y=230, hold=0.5, overlay=footprints(mark_at="@L0+0.3"),
          stamp={"text": {"ur": "MUJRIM!", "en": "GUILTY!"}, "on": "jamil", "line": 2, "y": 1560},
          lines=[ln("foxley", "Har doosre qadam ke saath ek gol nishaan!", "हर दूसरे क़दम के साथ एक गोल निशान!", "A round mark beside every second step!", sfx_before="reveal"),
                 ln("foxley", "Yeh chhadi ka nishaan hai. Aur chhadi sirf Chacha ke paas hai!", "ये छड़ी का निशान है। और छड़ी सिर्फ़ चाचा के पास है!",
                    "That's a walking stick. And only Chacha has one!"),
                 ln("jamil", "Arey... trophy bas dekhni thi!", "अरे... ट्रॉफ़ी बस देखनी थी!", "Oh... I only wanted to look at the trophy!", pose="guilty")]),
    {"set": "garden", "cast": [{"id": "nusrat", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.0}},
     "overlay": footprints(), "hold": 0.6},
  ]}

# ===================================================================== 5. Ek Maachis
LANTERN = (f'<svg viewBox="0 0 100 140" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
           f'<path d="M30 20 q20 -22 40 0" fill="none"/><rect x="28" y="20" width="44" height="14" rx="4" fill="#8A5A2B"/>'
           f'<path d="M24 34 h52 l-6 70 h-40z" fill="#CFE8F0"/><rect x="20" y="104" width="60" height="22" rx="6" fill="#8A5A2B"/></g>'
           f'<path d="M50 60 q8 14 0 26 q-8 -12 0 -26z" fill="#9AA" opacity="0.6"/></svg>')
CHULHA = (f'<svg viewBox="0 0 140 120" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
          f'<path d="M10 110 v-60 q0 -16 16 -16 h88 q16 0 16 16 v60z" fill="#B5651D"/><path d="M45 110 v-34 q25 -26 50 0 v34z" fill="#3A2410"/>'
          f'<path d="M30 34 h80 v-12 h-80z" fill="#8A5A2B"/><path d="M46 100 l18 -14 l14 10 l18 -12" stroke="#6B4A2A" stroke-width="7" fill="none"/></g></svg>')
CANDLE = (f'<svg viewBox="0 0 80 140" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
          f'<rect x="22" y="40" width="36" height="86" rx="6" fill="#FFF5E6"/><path d="M40 40 v-14" stroke-width="4"/>'
          f'<ellipse cx="40" cy="128" rx="34" ry="8" fill="#C98A1C"/></g></svg>')
MATCH = (f'<svg viewBox="0 0 160 70" width="100%" height="100%"><g stroke="{INK}" stroke-width="5" stroke-linejoin="round">'
         f'<rect x="6" y="14" width="96" height="48" rx="6" fill="#C8342B"/><rect x="16" y="24" width="76" height="28" rx="4" fill="#F2B134"/>'
         f'<rect x="96" y="28" width="56" height="9" rx="4" fill="#E3B467"/><ellipse cx="150" cy="32" rx="9" ry="8" fill="#8B1E1E"/></g></svg>')
FLAME = ('<svg viewBox="0 0 40 60" width="100%" height="100%"><path d="M20 58 C4 58 2 38 12 26 C12 36 18 36 18 30 C16 18 24 8 26 2 C30 20 38 30 36 44 C34 54 28 58 20 58Z" fill="#F2B134" stroke="#E8432B" stroke-width="4"/></svg>')


def kitchen_items(answer_at=None):
    html = panel(380)
    items = [(LANTERN, 90, 120, 168, "LALTAIN"), (CHULHA, 300, 190, 160, "CHULHA"), (CANDLE, 560, 100, 168, "MOMBATTI")]
    for k, (svg, x, w, h, label) in enumerate(items):
        html += f'<div id="{{sid}}-i{k}" style="position:absolute;left:{x}px;top:{PY + 60}px;width:{w}px;height:{h}px">{svg}</div>'
        html += numbadge(k + 1, x + w / 2 - 33, PY + 6, 66, 40)
        html += f'<div style="position:absolute;left:{x - 30}px;width:{w + 60}px;top:{PY + 240}px;text-align:center;font-weight:900;font-size:32px;color:{INK}">{label}</div>'
    html += (f'<div id="{{sid}}-m" style="position:absolute;left:770px;top:{PY + 120}px;width:220px;height:96px;transform-origin:50% 50%">{MATCH}'
             f'<div id="{{sid}}-fl" style="position:absolute;left:190px;top:-46px;width:40px;height:60px;opacity:0">{FLAME}</div></div>'
             f'<div style="position:absolute;left:760px;width:240px;top:{PY + 240}px;text-align:center;font-weight:900;font-size:32px;color:{INK}">1 TEELI</div>')
    js, sfx = [], []
    if answer_at:
        js += [f'tl.to("#{{sid}}-m", {{scale: 1.35, x: -60, y: -20, duration: 0.4, ease: "back.out(2)"}}, {answer_at});',
               f'tl.fromTo("#{{sid}}-fl", {{opacity: 0, scale: 0.2}}, {{opacity: 1, scale: 1.3, duration: 0.3, ease: "back.out(3)"}}, {answer_at}+0.4);',
               f'tl.to("#{{sid}}-fl", {{scale: 1.1, duration: 0.2, yoyo: true, repeat: 9, ease: "sine.inOut"}}, {answer_at}+0.7);']
        for k in range(3):
            js.append(f'tl.to("#{{sid}}-i{k}", {{opacity: 0.35, duration: 0.3}}, {answer_at}+0.2);')
        sfx += [["whoosh", answer_at], ["reveal", f"{answer_at}+0.4"]]
    return ov(html, js, sfx)


KCAM = {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.04}}
EPS["riddle_maachis"] = {"number": 305, "part": 1, "slug": "riddle_maachis", "title": {"ur": "EK MAACHIS", "en": "ONE MATCH"},
  "handle": "@AskFoxley", "music": {"bpm": 104, "gain": 0.5},
  "answer_note": "You light the matchstick first.",
  "shots": [
    {"set": "kitchen", "dark": 0.55, "cast": [{"id": "bunty", "x": 0.5}], "camera": KCAM, "sfx": [["sting", 0.0]], "caption_y": 1290, "hold": 0.1,
     "hook": {"text": "90% LOG GALAT JAWAB DETE HAIN!", "y": 110, "dur": 99}, "overlay": kitchen_items(),
     "lines": [ln("foxley", "Bijli chali gayi. Tumhare paas sirf ek maachis ki teeli hai.", "बिजली चली गई। तुम्हारे पास सिर्फ़ एक माचिस की तीली है।",
                  "The power's out. You have just one matchstick.")]},
    {"set": "kitchen", "dark": 0.55, "cast": [{"id": "bunty", "x": 0.5}], "camera": KCAM, "overlay": kitchen_items(), "timer": 3, "timer_y": 1500,
     "caption_y": 1290, "sfx": [["riser", 0.0]], "hold": 0.6,
     "cta": {"after_timer": True, "y": 160, "main": "1, 2 YA 3? COMMENT KARO!", "sub": "Jawab abhi aa raha hai..."},
     "lines": [ln("foxley", "Laltain, chulha ya mombatti... pehle kya jalaoge?", "लालटेन, चूल्हा या मोमबत्ती... पहले क्या जलाओगे?",
                  "Lantern, stove or candle... what do you light first?")]},
    {"set": "kitchen", "dark": 0.55, "cast": [{"id": "bunty", "x": 0.5}], "camera": KCAM, "overlay": kitchen_items(answer_at="@L0+0.3"),
     "caption_y": 1290, "hold": 0.5, "stamp": {"text": "HAHAHA!", "on": "bunty", "line": 1, "y": 130, "w": 560},
     "lines": [ln("foxley", "Sab se pehle... maachis ki teeli!", "सब से पहले... माचिस की तीली!", "First of all... the matchstick!"),
               ln("bunty", "Arey! Yeh to socha hi nahi!", "अरे! ये तो सोचा ही नहीं!", "Oh! I never thought of that!", pose="shocked")]},
    {"set": "kitchen", "dark": 0.55, "cast": [{"id": "bunty", "x": 0.5}], "camera": {"from": {"focus": [0.5, 0.62], "zoom": 1.0}, "to": {"focus": [0.5, 0.62], "zoom": 1.0}},
     "overlay": kitchen_items(), "hold": 0.6},
  ]}

for name, ep in EPS.items():
    json.dump(ep, open(os.path.join(ROOT, "episodes", f"{name}.json"), "w"), indent=2, ensure_ascii=False)
    print("wrote episodes/%s.json" % name)
