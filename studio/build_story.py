"""Build a story episode: several shots, sets, characters, voices, captions, music.

    .venv/bin/python studio/build_story.py episodes/s001_part1.json [--no-render] [--draft]

Episode JSON (see episodes/s001_part1.json):
{
  "number": 1, "part": 1, "title": "The Stolen Painting", "handle": "@AskFoxley",
  "music": {"bpm": 92, "gain": 0.5},
  "shots": [
    {"set": "mansion_living_room",
     "cast": [{"id": "penelope", "x": 0.62, "pose": "shocked"}],        # x: 0..1 across the set
     "camera": {"from": {"focus": [0.5, 0.33], "zoom": 1.9}, "to": {"focus": "penelope", "zoom": 1.15}},
     "title": "WHO STOLE THE PAINTING?",
     "lines": [{"who": "penelope", "say": "My painting! It's gone!", "pose": "shocked", "after": "faint"}],
     "timer": 5, "lineup": ["marco", "mia", "rocky"], "stamp": {"text": "GUILTY", "on": "marco", "line": 1},
     "highlight": "door", "cta": true, "hold": 0.5, "sfx": [["sting", 0.0]], "transition": "whoosh"}
  ]
}
A line's "pose" is held while it is spoken: the talk pose lip-syncs; any other pose is a
drawn expression (use it for shouts). "after" is the pose taken when the line ends.
"""
import argparse, json, os, random, shutil, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "studio"))
from lipsync import mouths  # noqa: E402
import audio  # noqa: E402


class LineCache:
    """Locked character voices, pre-rendered by studio/render_lines.py (run it with .venv-parler)."""

    def line(self, cid, text):
        sys.path.insert(0, os.path.join(ROOT, "studio"))
        from render_lines import cache_path, profile
        p = cache_path(cid, text, profile(cid)["voice"])
        if not os.path.exists(p):
            raise SystemExit(f"missing voice line for {cid}: {text!r}\n"
                             f"run: .venv-parler/bin/python studio/render_lines.py <episode.json>")
        a, sr = sf.read(p, dtype="float32")
        assert sr == VSR
        n = int(0.015 * VSR)  # 15 ms fades: no clicks where a line starts or stops
        a = a.copy()
        a[:n] *= np.linspace(0, 1, n)
        a[-n:] *= np.linspace(1, 0, n)
        return a

FPS = 30
W, H = 1080, 1920
VSR = 24000
FEET_Y = 0.87          # feet line on the frame (fraction of height) at zoom 1
BASE_H = 0.34          # Foxley's standing height as a fraction of the frame
GAP, PAD_IN, PAD_OUT = 0.22, 0.25, 0.35
CAPTION_TOP = 300

# on-screen text defaults (Roman Urdu/Hindi: readable for Pakistani and Indian viewers)
TEXT = {"cta1": "1, 2 YA 3? COMMENT KAREIN!", "sub1": "Jawab kal aayega · follow {handle}",
        "cta2": "AAP KA JAWAB SAHI THA?", "sub2": "Roz ek naya case · follow {handle}", "clue": "SURAAG"}

_PROFILES = {}


def profile(cid):
    if cid not in _PROFILES:
        _PROFILES[cid] = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))
    return _PROFILES[cid]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_rig(cid):
    return json.load(open(os.path.join(ROOT, "puppet", "cast", cid, "rig.json")))


def load_set(sid):
    p = os.path.join(ROOT, "sets", sid, "set.json")
    meta = json.load(open(p)) if os.path.exists(p) else {"size": [941, 1672], "floor_line": 0.6}
    return meta


# ---------------------------------------------------------------- voices
# ---------------------------------------------------------------- timeline
def plan(ep, voice):
    """lay every shot and line out in seconds; render the voice track"""
    t = 0.0
    shots, pieces, events = [], [], []
    for si, sh in enumerate(ep["shots"]):
        start = t
        t += PAD_IN if sh.get("lines") else 0.1
        lines = []
        for li, ln in enumerate(sh.get("lines", [])):
            a = voice.line(ln["who"], ln["say"])
            dur = len(a) / VSR
            lines.append({**ln, "start": t, "end": t + dur, "audio": a})
            if ln.get("sfx_after"):
                events.append((ln["sfx_after"], t + dur + 0.05))
            if ln.get("sfx_before"):
                events.append((ln["sfx_before"], max(t - 0.1, 0)))
            pieces.append((t, a))
            t += dur + GAP
        if sh.get("timer"):
            tstart = t
            t += sh["timer"]
            for k in range(int(sh["timer"])):
                events.append(("tick", tstart + k))
            sh = {**sh, "_timer_start": tstart}
        t += sh.get("hold", 0.0) + PAD_OUT
        for name, at in sh.get("sfx", []):
            events.append((name, start + at))
        if sh.get("transition") == "whoosh" and si > 0:
            events.append(("whoosh", max(start - 0.12, 0)))
        shots.append({**sh, "start": start, "end": t, "lines": lines})
    total = t
    track = np.zeros(int((total + 0.5) * VSR), np.float32)
    for at, a in pieces:
        i = int(at * VSR)
        track[i:i + len(a)] += a[: len(track) - i]
    return shots, track, events, total


# ---------------------------------------------------------------- html helpers
def camera_xy(focus, zoom):
    """world transform (x, y, scale) that puts focus (px) at the frame centre, clamped"""
    fx, fy = focus
    x = W / 2 - fx * zoom
    y = H * 0.5 - fy * zoom
    x = min(0, max(W - W * zoom, x))
    y = min(0, max(H - H * zoom, y))
    return round(x, 1), round(y, 1), round(zoom, 4)


def build_html(ep, shots, total):
    js, html = [], []
    add = js.append
    rnd = random.Random(f"story-{ep.get('number')}-{ep.get('part')}")
    vw = lambda fx: fx * W  # noqa: E731
    cap_html = []

    for si, sh in enumerate(shots):
        sid = f"s{si}"
        s0, s1 = round(sh["start"], 3), round(sh["end"], 3)
        dur = s1 - s0
        smeta = load_set(sh["set"])
        sw, shh = smeta["size"]
        kx, ky = W / sw, H / shh
        feet_y = H * sh.get("feet", FEET_Y)
        # ---- characters
        chars = {}
        ch_html = []
        for ci, c in enumerate(sh.get("cast", [])):
            rig = load_rig(c["id"])
            CW, CH = rig["canvas"]
            target = H * BASE_H * rig["height"] * c.get("scale", 1.0)
            s = target / rig["figure_height"]
            cx = vw(c["x"])
            left, top = cx - CW * s / 2, feet_y - CH * s
            face = c.get("face")
            flip = face is not None and rig["facing"] not in ("front", face)
            eid = f"{sid}c{ci}"
            chars[c["id"]] = {"eid": eid, "rig": rig, "head": (cx, feet_y - target * 0.82), "top": feet_y - target,
                              "pose": c.get("pose", rig["talk_pose"]), "s": s}
            layers = "".join(f'<img id="{eid}-p-{p}" class="part" src="cast/{c["id"]}/pose_{p}.png" alt="">' for p in rig["poses"])
            layers += "".join(f'<img id="{eid}-m-{m}" class="part" src="cast/{c["id"]}/mouth_{m}.png" alt="">' for m in rig["mouth"]["shapes"])
            ch_html.append(
                f'<div class="ch" style="left:{left:.1f}px;top:{top:.1f}px;width:{CW*s:.1f}px;height:{CH*s:.1f}px;z-index:{10+ci}">'
                f'<div class="fl{" flip" if flip else ""}"><div id="{eid}-br" class="br"><div id="{eid}-sq" class="sq">{layers}</div></div></div></div>')
            # idle life: breathing + sway, seeded and out of phase
            per = rnd.uniform(2.2, 3.2)
            add(f'tl.fromTo("#{eid}-br", {{scaleY: 1}}, {{scaleY: 1.014, duration: {per/2:.2f}, ease: "sine.inOut", yoyo: true, repeat: {int(dur/per*2)+2}}}, {s0});')
            sw_per = rnd.uniform(3.2, 4.6)
            amp = rnd.uniform(0.5, 0.9)
            add(f'tl.fromTo("#{eid}-br", {{rotation: {-amp:.2f}}}, {{rotation: {amp:.2f}, duration: {sw_per/2:.2f}, ease: "sine.inOut", yoyo: true, repeat: {int(dur/sw_per*2)+2}}}, {s0});')
        # ---- per-frame pose/mouth state for each character in this shot
        n0, n1 = int(s0 * FPS), int(s1 * FPS)
        for cid, info in chars.items():
            rig = info["rig"]
            pose = [info["pose"]] * (n1 - n0)
            mouth = ["none"] * (n1 - n0)
            for ln in sh["lines"]:
                if ln["who"] != cid:
                    continue
                a, b = int(ln["start"] * FPS) - n0, int(ln["end"] * FPS) - n0
                lp = ln.get("pose", rig["talk_pose"])
                for f in range(a, min(b, len(pose))):
                    pose[f] = lp
                if lp == rig["talk_pose"]:
                    ms = mouths(ln["audio"], VSR, FPS)
                    shapes = rig["mouth"]["shapes"]
                    for k, m in enumerate(ms):
                        if a + k >= len(mouth):
                            break
                        if m is None or m == "A":
                            continue
                        if shapes == ["open"]:
                            mouth[a + k] = "open"
                        else:
                            mouth[a + k] = {"D": "wide", "C": "medium", "E": "medium"}.get(m, "small")
                after = ln.get("after")
                if after:
                    for f in range(min(b, len(pose)), len(pose)):
                        pose[f] = after
            eid = info["eid"]
            prev_p, prev_m = None, "none"
            for f in range(len(pose)):
                t = round((n0 + f) / FPS, 4)
                if pose[f] != prev_p:
                    if prev_p:
                        add(f'tl.set("#{eid}-p-{prev_p}", {{opacity: 0}}, {t});')
                        add(f'tl.fromTo("#{eid}-sq", {{scaleY: 0.965, scaleX: 1.02}}, {{scaleY: 1, scaleX: 1, duration: 0.22, ease: "back.out(3)", immediateRender: false}}, {t});')
                    add(f'tl.set("#{eid}-p-{pose[f]}", {{opacity: 1}}, {t});')
                    prev_p = pose[f]
                if mouth[f] != prev_m:
                    if prev_m != "none":
                        add(f'tl.set("#{eid}-m-{prev_m}", {{opacity: 0}}, {t});')
                    if mouth[f] != "none":
                        add(f'tl.set("#{eid}-m-{mouth[f]}", {{opacity: 1}}, {t});')
                    prev_m = mouth[f]
            if prev_m != "none":
                add(f'tl.set("#{eid}-m-{prev_m}", {{opacity: 0}}, {s1});')

        # ---- set signs (text drawn in code so it is always spelled right)
        sign_html = []
        for key, sg in smeta.get("signs", {}).items():
            x0, y0, x1, y1 = sg["box"]
            if key == "facade":
                y0 = y0 + (y1 - y0) * 0.3
            bw, bh = (x1 - x0) * kx, (y1 - y0) * ky
            words = sg["text"].split()
            lines_txt = [sg["text"]] if len(words) <= 2 else [" ".join(words[:2]), " ".join(words[2:])]
            fs = min(bh / (len(lines_txt) * 1.25), bw * 0.9 / (max(len(t) for t in lines_txt) * 0.72))
            col = "#1F4E3A" if key == "facade" else "#B3261E"
            sign_html.append(f'<div id="{sid}-sign-{key}" class="sign" style="left:{x0*kx:.1f}px;top:{y0*ky:.1f}px;width:{bw:.1f}px;height:{bh:.1f}px;'
                             f'font-size:{fs:.1f}px;color:{col}">{"<br>".join(esc(t) for t in lines_txt)}</div>')
        if sh.get("highlight"):
            hk = sh["highlight"]
            x0, y0, x1, y1 = smeta["signs"][hk]["box"]
            pad = 14
            sign_html.append(f'<div id="{sid}-hl" class="hl" style="left:{x0*kx-pad:.1f}px;top:{y0*ky-pad:.1f}px;width:{(x1-x0)*kx+2*pad:.1f}px;height:{(y1-y0)*ky+2*pad:.1f}px"></div>')
            hl_at = s0 + sh.get("highlight_at", 0.3)
            add(f'tl.fromTo("#{sid}-hl", {{opacity: 0, scale: 1.4}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {hl_at:.3f});')
            add(f'tl.to("#{sid}-hl", {{scale: 1.06, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: {max(int((s1-hl_at)/0.4)-1, 1)}}}, {hl_at+0.35:.3f});')

        # ---- camera
        def resolve(spec):
            fc = spec.get("focus", [0.5, 0.5])
            if isinstance(fc, str):
                if fc.startswith("sign:"):
                    x0, y0, x1, y1 = smeta["signs"][fc[5:]]["box"]
                    fc_px = ((x0 + x1) / 2 * kx, (y0 + y1) / 2 * ky)
                elif fc == "group":
                    xs = [v["head"][0] for v in chars.values()]
                    fc_px = ((min(xs) + max(xs)) / 2, min(v["head"][1] for v in chars.values()) + 150)
                else:
                    fc_px = chars[fc]["head"]
                    fc_px = (fc_px[0], fc_px[1] + 120)
            else:
                fc_px = (fc[0] * W, fc[1] * H)
            return camera_xy(fc_px, spec.get("zoom", 1.0))
        cam = sh.get("camera", {"from": {"zoom": 1.0}, "to": {"zoom": 1.06}})
        x0c, y0c, z0 = resolve(cam.get("from", {"zoom": 1.0}))
        x1c, y1c, z1 = resolve(cam.get("to", cam.get("from", {"zoom": 1.0})))
        add(f'tl.fromTo("#{sid}-w", {{x: {x0c}, y: {y0c}, scale: {z0}}}, {{x: {x1c}, y: {y1c}, scale: {z1}, duration: {cam.get("dur", dur):.3f}, ease: "{cam.get("ease", "sine.inOut")}", immediateRender: false}}, {s0});')
        add(f'tl.set("#{sid}-w", {{x: {x0c}, y: {y0c}, scale: {z0}}}, {s0});')

        # ---- lineup numbers
        lu_html = []
        for k, cid in enumerate(sh.get("lineup", [])):
            hx, _ = chars[cid]["head"]
            ty = chars[cid]["top"] - 120
            lu_html.append(f'<div id="{sid}-n{k}" class="num" style="left:{hx-60:.1f}px;top:{ty:.1f}px">{k+1}</div>')
            add(f'tl.fromTo("#{sid}-n{k}", {{opacity: 0, scale: 0.3}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {s0 + 0.35 + 0.25*k:.3f});')
            js.append(f'audio_pop({s0 + 0.35 + 0.25*k:.3f});')

        # ---- stamp on a character
        st_html = ""
        stamp_overlay = ""
        if sh.get("stamp"):
            stp = sh["stamp"]
            on = chars[stp["on"]]
            at = sh["lines"][stp["line"]]["start"] if "line" in stp else s0 + stp.get("at", 0.5)
            hx, hy = on["head"]
            stamp_overlay = f'<div id="{sid}-stamp" class="stamp" style="left:{(W-460)/2:.0f}px;top:{stp.get("y", 1240)}px">{esc(stp["text"])}</div>'
            add(f'tl.fromTo("#{sid}-stamp", {{opacity: 0, scale: 2.6, rotation: -24}}, {{opacity: 1, scale: 1, rotation: -11, duration: 0.25, ease: "power4.in"}}, {at:.3f});')
            add(f'tl.fromTo("#{sid}-k", {{scale: 1.05}}, {{scale: 1, duration: 0.35, ease: "power3.out", immediateRender: false}}, {at+0.25:.3f});')
            js.append(f'audio_stamp({at+0.22:.3f});')

        bg = f'<img class="bg" src="sets/{sh["set"]}.png" alt="">'
        html.append(f'<div id="{sid}" class="shot"><div id="{sid}-k" class="shake"><div id="{sid}-w" class="world">{bg}{"".join(sign_html)}{"".join(ch_html)}{"".join(lu_html)}{st_html}</div></div></div>')
        add(f'tl.set("#{sid}", {{opacity: 1}}, {s0}); tl.set("#{sid}", {{opacity: 0}}, {s1});')
        if stamp_overlay:
            html.append(stamp_overlay)
            add(f'tl.set("#{sid}-stamp", {{opacity: 0}}, {s1});')

        # ---- frame overlays: title, timer, cta, answer
        if sh.get("title"):
            html.append(f'<div id="{sid}-title" class="title"><span>{esc(sh["title"])}</span></div>')
            ta = s0 + sh.get("title_at", 0.1)
            add(f'tl.fromTo("#{sid}-title", {{opacity: 0, scale: 0.5}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.2)"}}, {ta:.3f});')
            add(f'tl.to("#{sid}-title", {{opacity: 0, duration: 0.25}}, {min(ta + sh.get("title_dur", 2.6), s1 - 0.05):.3f});')
        if sh.get("timer"):
            secs = int(sh["timer"])
            t0 = sh["_timer_start"]
            digits = "".join(f'<div id="{sid}-tn{k}" class="tnum">{secs-k}</div>' for k in range(secs))
            html.append(f'<div id="{sid}-timer" class="timer"><div class="badge">{digits}</div><div class="bar"><div id="{sid}-fill" class="fill"></div></div></div>')
            add(f'tl.fromTo("#{sid}-timer", {{opacity: 0, y: -30}}, {{opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)"}}, {t0:.3f});')
            add(f'tl.fromTo("#{sid}-fill", {{scaleX: 1}}, {{scaleX: 0, duration: {secs}, ease: "none"}}, {t0:.3f});')
            for k in range(secs):
                add(f'tl.set("#{sid}-tn{k}", {{opacity: 1}}, {t0+k:.3f}); tl.fromTo("#{sid}-tn{k}", {{scale: 1.4}}, {{scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t0+k:.3f}); tl.set("#{sid}-tn{k}", {{opacity: 0}}, {t0+k+1:.3f});')
            add(f'tl.to("#{sid}-timer", {{opacity: 0, duration: 0.2}}, {t0+secs:.3f});')
        if sh.get("cta"):
            c = sh["cta"] if isinstance(sh["cta"], dict) else {}
            main = c.get("main", TEXT["cta1"] if ep.get("part", 1) == 1 else TEXT["cta2"])
            sub = c.get("sub", (TEXT["sub1"] if ep.get("part", 1) == 1 else TEXT["sub2"]).format(handle=ep.get("handle", "@AskFoxley")))
            cy = f' style="top:{c["y"]}px"' if "y" in c else ""
            html.append(f'<div id="{sid}-cta" class="cta"{cy}><div class="cmain">{esc(main)}</div><div class="csub">{esc(sub)}</div></div>')
            ca = (sh["_timer_start"] + sh["timer"]) if c.get("after_timer") and sh.get("timer") else s0 + c.get("at", 0.3)
            add(f'tl.fromTo("#{sid}-cta", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.2)"}}, {ca:.3f});')
            if si < len(shots) - 1:
                add(f'tl.set("#{sid}-cta", {{opacity: 0}}, {s1});')
        if sh.get("answer"):
            a = sh["answer"]
            ay = f' style="top:{a["y"]}px"' if "y" in a else ""
            html.append(f'<div id="{sid}-ans" class="ans"{ay}><div class="alab">{esc(a.get("label", TEXT["clue"]))}</div><div class="atext">{esc(a["text"])}</div></div>')
            aa = s0 + a.get("at", 0.3)
            add(f'tl.fromTo("#{sid}-ans", {{opacity: 0, y: -40}}, {{opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)"}}, {aa:.3f});')
            add(f'tl.set("#{sid}-ans", {{opacity: 0}}, {s1});')

        # ---- captions: phrase by phrase, the current word highlighted
        for li, ln in enumerate(sh["lines"]):
            words = ln.get("caption", ln["say"]).split()
            weights = np.array([len(w) + 2 for w in words], float)
            span = (ln["end"] - ln["start"]) * 0.96
            starts = ln["start"] + np.concatenate([[0], np.cumsum(weights)[:-1]]) / weights.sum() * span
            chunks, cur = [], []
            for wi, w in enumerate(words):
                cur.append(wi)
                if len(cur) >= 4 or w.endswith((".", "!", "?", ",")) and len(cur) >= 2:
                    chunks.append(cur)
                    cur = []
            if cur:
                chunks.append(cur)
            prof = profile(ln["who"])
            col = prof.get("accent", "#E8762B")
            name = prof.get("label", prof["name"].upper())
            for ki, ch in enumerate(chunks):
                cid = f"{sid}l{li}k{ki}"
                spans = "".join(f'<span id="{cid}w{wi}" class="w">{esc(words[wi])}</span> ' for wi in ch)
                cy_style = f' style="top:{sh["caption_y"]}px"' if sh.get("caption_y") else ""
                cap_html.append(f'<div id="{cid}" class="cap"{cy_style}><div class="who" style="background:{col}">{esc(name)}</div><div class="ctext">{spans}</div></div>')
                c_on = starts[ch[0]]
                c_off = starts[chunks[ki + 1][0]] if ki + 1 < len(chunks) else ln["end"] + 0.15
                add(f'tl.set("#{cid}", {{opacity: 1}}, {c_on:.3f}); tl.set("#{cid}", {{opacity: 0}}, {c_off:.3f});')
                for wi in ch:
                    add(f'tl.set("#{cid}w{wi}", {{color: "#FFD23F"}}, {starts[wi]:.3f});')
                    if wi + 1 < len(words) and wi != ch[-1]:
                        add(f'tl.set("#{cid}w{wi}", {{color: "#FFFFFF"}}, {starts[wi+1]:.3f});')

    body = "\n".join(html + cap_html)
    tl_js = "\n      ".join(x for x in js if not x.startswith("audio_"))
    return f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      :root {{ --ink: #2B2B2B; --teal: #1F4E5F; --orange: #E8762B; --mustard: #F2B134; --red: #C8342B; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #1b1b1b; }}
      #root {{ position: relative; width: 100%; height: 100%; font-family: "Nunito", sans-serif; overflow: hidden; }}
      .shot {{ position: absolute; inset: 0; opacity: 0; overflow: hidden; }}
      .shake {{ position: absolute; inset: 0; transform-origin: 50% 45%; }}
      .world {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; }}
      .bg {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      .ch {{ position: absolute; }}
      .fl, .br, .sq {{ position: absolute; inset: 0; }}
      .fl.flip {{ transform: scaleX(-1); }}
      .br, .sq {{ transform-origin: 50% 100%; }}
      .part {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; opacity: 0; }}
      .sign {{ position: absolute; display: flex; align-items: center; justify-content: center; text-align: center;
               font-weight: 900; line-height: 1.12; letter-spacing: 0.02em; white-space: nowrap; }}
      .hl {{ position: absolute; border: 8px solid #FFD23F; border-radius: 18px; box-shadow: 0 0 0 6px rgba(0,0,0,0.35); opacity: 0; }}
      .num {{ position: absolute; width: 120px; height: 120px; border-radius: 50%; background: var(--mustard); border: 8px solid var(--ink);
              display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 70px; color: var(--ink); opacity: 0; z-index: 50; }}
      .stamp {{ position: absolute; width: 460px; padding: 12px 0; text-align: center; border: 12px solid var(--red); border-radius: 22px;
                color: var(--red); font-weight: 900; font-size: 92px; letter-spacing: 0.06em; background: rgba(255,255,255,0.85); opacity: 0; z-index: 88; }}
      .title {{ position: absolute; left: 60px; right: 60px; top: 560px; text-align: center; opacity: 0; z-index: 80; }}
      .title span {{ display: inline-block; background: var(--red); color: #fff; font-weight: 900; font-size: 84px; line-height: 1.05;
                     padding: 22px 34px; border-radius: 30px; border: 9px solid var(--ink); box-shadow: 0 14px 0 var(--ink); }}
      .timer {{ position: absolute; left: 120px; right: 120px; top: 620px; display: flex; align-items: center; gap: 22px; opacity: 0; z-index: 80; }}
      .badge {{ position: relative; width: 140px; height: 140px; flex: none; border-radius: 50%; background: var(--red); border: 8px solid var(--ink); }}
      .tnum {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 900; font-size: 82px; opacity: 0; }}
      .bar {{ flex: 1; height: 48px; border: 8px solid var(--ink); border-radius: 30px; background: #fff; overflow: hidden; }}
      .fill {{ width: 100%; height: 100%; background: linear-gradient(90deg, var(--orange), var(--mustard)); transform-origin: 0 50%; }}
      .cta {{ position: absolute; left: 70px; right: 70px; top: 560px; text-align: center; opacity: 0; z-index: 85; }}
      .cmain {{ display: inline-block; background: var(--orange); color: #fff; font-weight: 900; font-size: 66px; padding: 18px 36px;
                border-radius: 28px; border: 8px solid var(--ink); box-shadow: 0 10px 0 var(--ink); }}
      .csub {{ display: inline-block; margin-top: 18px; background: rgba(255,250,240,0.95); color: var(--ink); font-weight: 800; font-size: 34px;
               padding: 8px 24px; border-radius: 30px; border: 5px solid var(--ink); }}
      .ans {{ position: absolute; left: 70px; right: 70px; top: 520px; background: var(--mustard); border: 8px solid var(--ink); border-radius: 36px;
              box-shadow: 0 12px 0 var(--ink); padding: 20px 34px 28px; text-align: center; opacity: 0; z-index: 85; }}
      .alab {{ font-weight: 900; font-size: 34px; letter-spacing: 0.14em; color: var(--teal); }}
      .atext {{ font-weight: 900; font-size: 58px; line-height: 1.12; color: var(--ink); }}
      .cap {{ position: absolute; left: 50px; right: 50px; top: {CAPTION_TOP}px; text-align: center; opacity: 0; z-index: 90; }}
      .who {{ display: inline-block; color: #fff; font-weight: 900; font-size: 32px; letter-spacing: 0.08em; padding: 6px 20px;
              border-radius: 20px; border: 5px solid var(--ink); margin-bottom: 10px; }}
      .ctext {{ font-weight: 900; font-size: 74px; line-height: 1.1; color: #fff;
                text-shadow: -5px -5px 0 #222, 5px -5px 0 #222, -5px 5px 0 #222, 5px 5px 0 #222, 0 7px 0 #222, 0 9px 12px rgba(0,0,0,0.45); }}
      .w {{ color: #FFFFFF; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="{W}" data-height="{H}">
{body}
      <audio id="mix" class="clip" src="mix.wav" data-start="0" data-duration="{total:.3f}" data-track-index="1" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {tl_js}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
""", [(x.split("(")[0].replace("audio_", ""), float(x.split("(")[1].rstrip(");"))) for x in js if x.startswith("audio_")]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--draft", action="store_true")
    a = ap.parse_args()
    ep = json.load(open(a.episode))
    name = f"story_{int(ep['number']):03d}_part{int(ep['part'])}"
    work = os.path.join(ROOT, "build", name)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.join(work, "vendor"))
    os.makedirs(os.path.join(work, "sets"))
    shutil.copy(os.path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), os.path.join(work, "vendor"))
    used_cast = {c["id"] for sh in ep["shots"] for c in sh.get("cast", [])}
    for cid in used_cast:
        shutil.copytree(os.path.join(ROOT, "puppet", "cast", cid), os.path.join(work, "cast", cid))
    for sid in {sh["set"] for sh in ep["shots"]}:
        src = os.path.join(ROOT, "sets", sid, "background.png")
        if not os.path.exists(src):
            src = os.path.join(ROOT, "source", "background.png") if sid == "foxley_study" else src
        shutil.copy(src, os.path.join(work, "sets", f"{sid}.png"))

    print("1/4 voices ...")
    shots, track, events, total = plan(ep, LineCache())
    print(f"    {len(shots)} shots, {total:.1f}s")
    print("2/4 composition ...")
    html, extra = build_html(ep, shots, total)
    open(os.path.join(work, "index.html"), "w").write(html)
    print("3/4 music + mix ...")
    m = ep.get("music", {})
    music = audio.music_mystery(total + 0.5, bpm=m.get("bpm", 92), seed=int(ep["number"]))
    events = events + extra
    audio.mix(track, VSR, music, events, os.path.join(work, "mix.wav"), music_gain=m.get("gain", 0.5))
    if a.no_render:
        print("built", work)
        return
    print("4/4 rendering ...")
    out = os.path.join(ROOT, "output", name + ".mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    env = {**os.environ, "PUPPETEER_EXECUTABLE_PATH": "/opt/pw-browsers/chromium", "HYPERFRAMES_SKIP_SKILLS": "1"}
    subprocess.run(["npx", "hyperframes", "render", ".", "-o", out, "--fps", str(FPS), "--quiet",
                    "--quality", "draft" if a.draft else "looks"], cwd=work, env=env, check=True)
    print("done:", out)


if __name__ == "__main__":
    main()
