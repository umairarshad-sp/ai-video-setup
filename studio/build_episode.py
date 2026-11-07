"""Build one Foxley riddle video from an episode script.

    .venv/bin/python studio/build_episode.py episodes/001_part1.json [--puppet puppet/placeholder] [--no-render]

Steps: Kokoro voiceover per line -> one voice track -> lip sync -> per-frame
puppet states (expression, blinks, mouth) -> HyperFrames composition -> MP4.
"""
import argparse, json, os, random, shutil, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "studio"))
from lipsync import mouths  # noqa: E402

FPS = 30
SR = 24000
W, H = 1080, 1920
PUPPET_SCALE = 0.6
PUPPET_POS = (250, 1010)  # top-left of the 900x1300 puppet canvas on the 1080x1920 frame
LEAD_IN, GAP, TAIL = 0.35, 0.3, 0.8


# ---------------------------------------------------------------- audio
def make_voice(ep, workdir):
    from kokoro_onnx import Kokoro
    tts = Kokoro(os.path.join(ROOT, "models/kokoro-v1.0.onnx"), os.path.join(ROOT, "models/voices-v1.0.bin"))
    voice, speed = ep.get("voice", "am_puck"), ep.get("speed", 1.0)
    pieces, timeline, t = [np.zeros(int(LEAD_IN * SR), dtype=np.float32)], [], LEAD_IN
    for i, seg in enumerate(ep["segments"]):
        if "say" in seg:
            audio, sr = tts.create(seg["say"], voice=seg.get("voice", voice), speed=seg.get("speed", speed), lang="en-us")
            assert sr == SR
            audio = audio.astype(np.float32)
            dur = len(audio) / SR
            timeline.append({**seg, "start": t, "end": t + dur, "audio": audio})
            pieces += [audio, np.zeros(int(GAP * SR), dtype=np.float32)]
            t += dur + GAP
        else:
            dur = seg.get("timer", seg.get("pause", 0.5))
            timeline.append({**seg, "start": t, "end": t + dur})
            pieces.append(np.zeros(int(dur * SR), dtype=np.float32))
            t += dur
    pieces.append(np.zeros(int(TAIL * SR), dtype=np.float32))
    track = np.concatenate(pieces)
    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.89  # about -1 dBFS
    sf.write(os.path.join(workdir, "voice.wav"), track, SR)
    return timeline, len(track) / SR


# ---------------------------------------------------------------- puppet states
def frame_states(ep, rig, timeline, duration):
    n = int(round(duration * FPS))
    exprs = rig["expressions"]
    expr = ["neutral"] * n
    talk = [None] * n
    cur = timeline[0].get("expression", "neutral") if timeline else "neutral"
    for seg in timeline:
        a, b = int(seg["start"] * FPS), int(seg["end"] * FPS)
        cur = seg.get("expression", cur)
        for f in range(a, n):
            expr[f] = cur
        if "audio" in seg:
            ms = mouths(seg["audio"], SR, FPS)
            for k, m in enumerate(ms):
                if a + k < n:
                    talk[a + k] = m
    # blinks every 2.2-4.5 s, 4 frames long
    rnd = random.Random(f"{ep.get('number')}-{ep.get('part')}")
    blink = [False] * n
    f = int(rnd.uniform(1.0, 2.0) * FPS)
    while f < n:
        for k in range(4):
            if f + k < n:
                blink[f + k] = True
        f += int(rnd.uniform(2.2, 4.5) * FPS)
    if rig.get("kind") == "bust":
        return bust_states(rig, timeline, n, talk, blink)
    skip = set(rig["blink"]["skip_when"])
    states = []
    for f in range(n):
        e = exprs[expr[f]]
        eyes = e["eyes"]
        if blink[f] and eyes not in skip:
            eyes = rig["blink"]["closed"]
        states.append({"eyes": eyes, "brows": e["brows"], "armR": e["armR"],
                       "mouth": talk[f] or e["idle_mouth"]})
    return states, expr


def bust_states(rig, timeline, n, talk, blink):
    """Talk/react puppet: the front-facing bust lip-syncs while Foxley speaks; timer and
    pause segments cut to the reaction pose for that segment's expression."""
    poses = rig["expressions"]
    body = ["talk"] * n
    for i, seg in enumerate(timeline):
        a, b = int(seg["start"] * FPS), int(seg["end"] * FPS)
        if "say" in seg:
            continue
        pose = poses.get(seg.get("expression") or "neutral")
        if pose:
            # a pause right before the first line also covers the lead-in
            a = 0 if i == 0 else a
            for f in range(a, min(b, n)):
                body[f] = pose
    # the last pose holds through the tail of the video
    last = timeline[-1] if timeline else None
    if last is not None and "say" not in last and poses.get(last.get("expression") or "neutral"):
        for f in range(int(last["end"] * FPS), n):
            body[f] = poses[last["expression"]]
    states = []
    for f in range(n):
        talking = body[f] == "talk"
        states.append({
            "body": body[f],
            "mouth": (talk[f] or "X") if talking else "none",
            "eyes": "closed" if (talking and blink[f]) else "none",
        })
    return states, body


# ---------------------------------------------------------------- html
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_html(ep, rig, timeline, duration, states, expr):
    js = []
    add = js.append
    # --- puppet layers
    imgs = []
    for L in rig["layers"]:
        for v, fn in L["files"].items():
            imgs.append((L["group"], L["slot"], v, fn))
    groups = {"tail": [], "body": [], "head": [], "front": []}
    for g, slot, v, fn in imgs:
        groups[g].append(f'<img id="p-{slot}-{v}" class="part" src="puppet/{fn}" alt="">')
    cw, ch = rig.get("canvas", [900, 1300])
    bottom = [cw // 2, ch]
    pv = {"tail": bottom, "feet": bottom, "neck": bottom, **rig.get("pivots", {})}

    # --- initial visibility and per-frame diffs ("none" = slot shows nothing)
    add("// puppet: fixed layers")
    for slot, v in rig.get("fixed", {}).items():
        add(f'tl.set("#p-{slot}-{v}", {{opacity: 1}}, 0);')
    prev = {}
    for f, st in enumerate(states):
        t = round(f / FPS, 4)
        for slot, v in st.items():
            if prev.get(slot) != v:
                if prev.get(slot, "none") != "none":
                    add(f'tl.set("#p-{slot}-{prev[slot]}", {{opacity: 0}}, {t});')
                if v != "none":
                    add(f'tl.set("#p-{slot}-{v}", {{opacity: 1}}, {t});')
                prev[slot] = v

    # --- idle motion (seekable, deterministic)
    add("// idle motion")
    cyc = 1.6
    reps = int(duration / cyc) + 1
    if rig.get("kind") == "bust":
        add(f'tl.fromTo("#g-body", {{scaleY: 1, rotation: -1}}, {{scaleY: 1.012, rotation: 1, duration: {cyc}, ease: "sine.inOut", yoyo: true, repeat: {reps}}}, 0);')
    else:
        add(f'tl.fromTo("#g-body, #g-front", {{scaleY: 1}}, {{scaleY: 1.014, duration: {cyc/2}, ease: "sine.inOut", yoyo: true, repeat: {reps*2}}}, 0);')
        add(f'tl.fromTo("#g-head", {{rotation: -1.6, y: 0}}, {{rotation: 1.6, y: 4, duration: {cyc*1.25}, ease: "sine.inOut", yoyo: true, repeat: {int(duration/(cyc*1.25))+1}}}, 0);')
        add(f'tl.fromTo("#g-tail", {{rotation: -5}}, {{rotation: 6, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: {int(duration/1.1)+1}}}, 0);')
    # little hop on each expression change
    last = expr[0] if expr else None
    for f in range(1, len(expr)):
        if expr[f] != last:
            t = round(f / FPS, 3)
            add(f'tl.to("#fox-hop", {{y: -26, duration: 0.12, ease: "power2.out", yoyo: true, repeat: 1}}, {t});')
            last = expr[f]

    # --- graphics events
    add("// graphics")
    add('tl.fromTo("#header", {opacity: 0, y: -30}, {opacity: 1, y: 0, duration: 0.4, ease: "back.out(2)"}, 0.05);')
    add('tl.fromTo("#fox-in", {opacity: 0, y: 120}, {opacity: 1, y: 0, duration: 0.5, ease: "back.out(1.6)"}, 0.1);')
    add(f'tl.to(".qm", {{rotation: 12, duration: {duration/2:.2f}, ease: "sine.inOut", yoyo: true, repeat: 1}}, 0);')
    timer_html = ""
    for seg in timeline:
        t0, t1 = round(seg["start"], 3), round(seg["end"], 3)
        show = seg.get("show")
        if show == "riddle":
            add(f'tl.fromTo("#card", {{opacity: 0, scale: 0.8}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.8)"}}, {t0});')
        elif show == "cta":
            add(f'tl.fromTo("#cta", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2.2)"}}, {t0});')
            add(f'tl.fromTo("#cta-arrow", {{y: 0}}, {{y: 14, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: {int((duration-t0)/0.35)}}}, {t0+0.35:.3f});')
        elif show == "answer":
            add(f'tl.to("#card-riddle", {{opacity: 0, scale: 0.9, duration: 0.25}}, {t0});')
            add(f'tl.fromTo("#answer", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.4)"}}, {t0+0.1:.3f});')
        elif show == "explain":
            add(f'tl.fromTo("#explain", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.35}}, {t0});')
        elif show == "stamp":
            add(f'tl.fromTo("#stamp", {{opacity: 0, scale: 2.6, rotation: -25}}, {{opacity: 1, scale: 1, rotation: -12, duration: 0.28, ease: "power4.in"}}, {t0});')
            add(f'tl.fromTo("#stage", {{x: 0}}, {{x: 10, duration: 0.05, yoyo: true, repeat: 5}}, {t0+0.28:.3f});')
        if "timer" in seg:
            secs = int(seg["timer"])
            add(f'tl.fromTo("#timer", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}}, {t0});')
            add(f'tl.fromTo("#timer-fill", {{scaleX: 1}}, {{scaleX: 0, duration: {secs}, ease: "none"}}, {t0});')
            add(f'tl.to("#timer", {{opacity: 0, scale: 0.8, duration: 0.25}}, {t1});')
            digits = []
            for k in range(secs):
                did = f"tn{k}"
                digits.append(f'<div id="{did}" class="tnum">{secs-k}</div>')
                ts = round(t0 + k, 3)
                add(f'tl.set("#{did}", {{opacity: 1}}, {ts});')
                add(f'tl.fromTo("#{did}", {{scale: 1.35}}, {{scale: 1, duration: 0.3, ease: "back.out(3)"}}, {ts});')
                add(f'tl.set("#{did}", {{opacity: 0}}, {round(min(ts+1, t1), 3)});')
            timer_html = (
                '<div id="timer"><div id="timer-badge">' + "".join(digits) + '</div>'
                '<div id="timer-bar"><div id="timer-fill"></div></div></div>')

    num = int(ep.get("number", 1))
    part = int(ep.get("part", 1))
    diff = int(ep.get("difficulty", 3))
    dots = "".join(f'<span class="dot{" on" if i < diff else ""}"></span>' for i in range(5))
    sub = "CAN YOU SOLVE IT?" if part == 1 else "THE ANSWER"
    handle = esc(ep.get("handle", "@AskFoxley"))
    cta_main = esc(ep.get("cta", "COMMENT YOUR ANSWER" if part == 1 else "DID YOU GET IT RIGHT?"))
    cta_sub = esc(ep.get("cta_sub", f"Answer drops tomorrow · follow {handle}" if part == 1 else f"Follow {handle} for daily riddles"))
    qms = "".join(
        f'<div class="qm" style="left:{x}px;top:{y}px;font-size:{fs}px">?</div>'
        for x, y, fs in [(60, 420, 220), (860, 300, 170), (900, 1180, 240), (40, 1350, 160), (760, 1700, 200), (120, 1760, 130)])
    answer_html = ""
    if ep.get("answer"):
        answer_html = (f'<div id="answer"><div class="label">ANSWER</div><div id="answer-text">{esc(ep["answer"])}</div>'
                       + (f'<div id="explain">{esc(ep["explanation"])}</div>' if ep.get("explanation") else "")
                       + '</div>')

    tl_js = "\n      ".join(js)
    disp = rig.get("display", {"left": PUPPET_POS[0], "top": PUPPET_POS[1], "scale": PUPPET_SCALE})
    has_bg = ep.get("_bg", False)
    bg_html = '<img id="bg-img" src="bg.png" alt=""><div id="bg-tint"></div>' if has_bg else qms
    desk_html = f'<div id="desk"><div id="desk-top"></div><div id="desk-text">{handle} &#183; A NEW RIDDLE EVERY DAY</div></div>' if rig.get("desk") else ""
    origin = lambda p: f"{p[0]}px {p[1]}px"  # noqa: E731
    return f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      :root {{
        --ground: #FFF4E0; --ink: #2B2B2B; --teal: #1F4E5F; --orange: #E8762B;
        --mustard: #F2B134; --cream: #F5E6CC; --red: #C8342B;
        --font-display: "Nunito", sans-serif;
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: var(--ground); }}
      #root {{ width: 100%; height: 100%; position: relative; font-family: var(--font-display); color: var(--ink); }}
      #bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 50% 38%, #FFFDF6 0%, #FFF4E0 55%, #F7E3C2 100%); }}
      .qm {{ position: absolute; font-weight: 900; color: var(--teal); opacity: 0.07; line-height: 1; }}
      #stage {{ position: absolute; inset: 0; }}
      #header {{ position: absolute; left: 0; right: 0; top: 230px; display: flex; flex-direction: column; align-items: center; gap: 14px; }}
      #pill {{ background: var(--teal); color: #fff; font-weight: 900; font-size: 46px; letter-spacing: 0.04em;
               padding: 14px 40px; border-radius: 60px; border: 6px solid var(--ink); }}
      #pill b {{ color: var(--mustard); }}
      #sub {{ font-weight: 800; font-size: 34px; letter-spacing: 0.08em; display: flex; align-items: center; gap: 18px;
             background: rgba(255,248,236,0.92); padding: 8px 26px; border-radius: 40px; border: 5px solid var(--ink); }}
      .dot {{ display: inline-block; width: 22px; height: 22px; border-radius: 50%; border: 4px solid var(--ink); background: #fff; margin: 0 3px; }}
      .dot.on {{ background: var(--orange); }}
      #card {{ position: absolute; left: 70px; right: 70px; top: 430px; height: 410px; opacity: 0; }}
      #card-riddle {{ position: absolute; inset: 0; background: #fff; border: 8px solid var(--ink); border-radius: 44px;
                      box-shadow: 0 14px 0 var(--ink); display: flex; align-items: center; justify-content: center;
                      padding: 40px 54px; text-align: center; font-weight: 900; font-size: {ep.get("riddle_size", 64)}px; line-height: 1.18; }}
      #answer {{ position: absolute; left: 0; right: 0; top: 40px; background: var(--mustard); border: 8px solid var(--ink);
                 border-radius: 40px; box-shadow: 0 12px 0 var(--ink); padding: 26px 40px 34px; text-align: center; opacity: 0; }}
      #answer .label {{ font-weight: 900; font-size: 34px; letter-spacing: 0.14em; color: var(--teal); }}
      #answer-text {{ font-weight: 900; font-size: 92px; line-height: 1.05; }}
      #explain {{ font-weight: 700; font-size: 38px; line-height: 1.25; margin-top: 14px; opacity: 0; }}
      #timer {{ position: absolute; left: 140px; right: 140px; top: 865px; display: flex; align-items: center; gap: 24px; opacity: 0; }}
      #timer-badge {{ position: relative; width: 130px; height: 130px; flex: none; border-radius: 50%; background: var(--red);
                      border: 7px solid var(--ink); }}
      .tnum {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #fff;
               font-weight: 900; font-size: 74px; opacity: 0; }}
      #timer-bar {{ flex: 1; height: 44px; border: 7px solid var(--ink); border-radius: 30px; background: #fff; overflow: hidden; }}
      #timer-fill {{ width: 100%; height: 100%; background: linear-gradient(90deg, var(--orange), var(--mustard)); transform-origin: 0 50%; }}
      #cta {{ position: absolute; left: 90px; right: 90px; top: 860px; text-align: center; opacity: 0; }}
      #cta-main {{ display: inline-block; background: var(--orange); color: #fff; font-weight: 900; font-size: 50px;
                   padding: 14px 36px; border-radius: 26px; border: 7px solid var(--ink); box-shadow: 0 8px 0 var(--ink); }}
      #cta-sub {{ display: inline-block; font-weight: 800; font-size: 32px; margin-top: 16px; background: rgba(255,248,236,0.92);
                  padding: 6px 22px; border-radius: 30px; }}
      #cta-arrow {{ display: none; font-weight: 900; font-size: 60px; line-height: 1; color: var(--orange); }}
      #stamp {{ position: absolute; left: 700px; top: 395px; padding: 10px 26px; text-align: center; line-height: 1; border: 10px solid var(--red); border-radius: 18px;
                color: var(--red); font-weight: 900; font-size: 56px; letter-spacing: 0.04em; opacity: 0; background: rgba(255,255,255,0.75); }}
      #fox-wrap {{ position: absolute; left: {disp["left"]}px; top: {disp["top"]}px; width: {cw}px; height: {ch}px;
                   transform: scale({disp["scale"]}); transform-origin: 0 0; }}
      #fox-in, #fox-hop, .grp {{ position: absolute; inset: 0; }}
      #g-tail {{ transform-origin: {origin(pv["tail"])}; }}
      #g-body, #g-front {{ transform-origin: {origin(pv["feet"])}; }}
      #g-head {{ transform-origin: {origin(pv["neck"])}; }}
      .part {{ position: absolute; left: 0; top: 0; width: {cw}px; height: {ch}px; opacity: 0; }}
      #bg-img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; filter: blur(3px) saturate(0.9); transform: scale(1.03); }}
      #bg-tint {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(255,244,224,0.55) 0%, rgba(255,244,224,0.25) 45%, rgba(255,244,224,0.1) 100%); }}
      #desk {{ position: absolute; left: -20px; right: -20px; top: 1600px; bottom: -20px; background: var(--teal); border-top: 10px solid var(--ink); }}
      #desk-top {{ height: 34px; background: var(--mustard); border-bottom: 8px solid var(--ink); }}
      #desk-text {{ color: #fff; font-weight: 900; font-size: 34px; letter-spacing: 0.06em; text-align: center; margin-top: 34px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{duration:.3f}" data-width="{W}" data-height="{H}">
      <div id="bg">{bg_html}</div>
      <div id="stage">
        <div id="header"><div id="pill">RIDDLE <b>#{num:03d}</b></div><div id="sub">{sub} <span>{dots}</span></div></div>
        <div id="card"><div id="card-riddle">{esc(ep.get("riddle", ""))}</div>{answer_html}</div>
        {timer_html}
        <div id="cta"><div id="cta-main">{cta_main}</div><div id="cta-sub">{cta_sub}</div><div id="cta-arrow">&#9660;</div></div>
        <div id="fox-wrap"><div id="fox-in"><div id="fox-hop">
          <div id="g-tail" class="grp">{"".join(groups["tail"])}</div>
          <div id="g-body" class="grp">{"".join(groups["body"])}</div>
          <div id="g-head" class="grp">{"".join(groups["head"])}</div>
          <div id="g-front" class="grp">{"".join(groups["front"])}</div>
        </div></div></div>
        {desk_html}
        <div id="stamp">CASE<br>CLOSED!</div>
      </div>
      <audio id="voice" class="clip" src="voice.wav" data-start="0" data-duration="{duration:.3f}" data-track-index="1" data-volume="1"></audio>
      {ep.get("_extra_audio", "")}
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
"""


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--puppet", default=os.path.join(ROOT, "puppet/foxley"))
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--background", help="background image (default: source/background.png)")
    ap.add_argument("--draft", action="store_true", help="faster, lower-quality render")
    a = ap.parse_args()

    ep = json.load(open(a.episode))
    rig = json.load(open(os.path.join(a.puppet, "rig.json")))
    name = f"foxley_{int(ep.get('number', 1)):03d}_part{int(ep.get('part', 1))}"
    work = os.path.join(ROOT, "build", name)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.join(work, "vendor"))
    shutil.copy(os.path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), os.path.join(work, "vendor"))
    shutil.copytree(a.puppet, os.path.join(work, "puppet"))
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
               "media": {"autoProxy": True}}, open(os.path.join(work, "hyperframes.json"), "w"), indent=2)

    bg = a.background or os.path.join(ROOT, "source", "background.png")
    if bg and os.path.exists(bg):
        shutil.copy(bg, os.path.join(work, "bg.png"))
        ep["_bg"] = True
    print("1/4 voiceover ...")
    timeline, duration = make_voice(ep, work)
    print(f"    {duration:.1f}s")
    print("2/4 lip sync + puppet states ...")
    states, expr = frame_states(ep, rig, timeline, duration)
    print("3/4 composition ...")
    open(os.path.join(work, "index.html"), "w").write(build_html(ep, rig, timeline, duration, states, expr))
    if a.no_render:
        print("built", work)
        return
    print("4/4 rendering ...")
    out = os.path.join(ROOT, "output", name + ".mp4")
    env = {**os.environ, "PUPPETEER_EXECUTABLE_PATH": "/opt/pw-browsers/chromium", "HYPERFRAMES_SKIP_SKILLS": "1"}
    cmd = ["npx", "hyperframes", "render", ".", "-o", out, "--fps", str(FPS), "--quiet",
           "--quality", "draft" if a.draft else "looks"]
    subprocess.run(cmd, cwd=work, env=env, check=True)
    print("done:", out)


if __name__ == "__main__":
    main()
