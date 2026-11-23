"""Shared code-drawn props for the riddle writers.

real_doors(): opens the doors painted in a background (sets/<id>/set.json -> "doors", in image pixels).
Before a door opens the painted door is what viewers see; opening it parts an arched "room" view from
the centre, showing what is behind. Use a camera that does not move (zoom 1.0) so the overlay stays on
the painted doors.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2B2B2B"
W, H = 1080, 1920


def set_meta(sid):
    return json.load(open(os.path.join(ROOT, "sets", sid, "set.json")))


def frame_rect(sid, box):
    m = set_meta(sid)
    sw, sh = m["size"]
    kx, ky = W / sw, H / sh
    x0, y0, x1, y1 = box
    return x0 * kx, y0 * ky, (x1 - x0) * kx, (y1 - y0) * ky


def pop(idx, t):
    return f'tl.fromTo("#{{sid}}-{idx}", {{opacity: 0, scale: 0.4}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(3)"}}, {t});'


def real_doors(sid, contents, labels=None, label_colors=None, open_at=(), cross_at=(), swap_at=(), show_open=(), numbers=True):
    """contents: list of SVG/HTML shown behind each door (index 0 = door 1).
    open_at:  [(door number, time expr)]          door parts to show its room
    cross_at: [(door number, time expr)]          a red X lands over the door
    swap_at:  [(door number, time expr, html)]    the room picture is replaced (e.g. the lion lies dead)
    show_open: door numbers that start already open (no animation)"""
    m = set_meta(sid)
    html, js, sfx = "", [], []
    for i, box in enumerate(m["doors"]):
        n = i + 1
        x, y, w, h = frame_rect(sid, box)
        start = 1 if n in show_open else 0
        html += (f'<div id="{{sid}}-room{n}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;'
                 f'border-radius:50% 50% 4px 4px / 26% 26% 4px 4px;overflow:hidden;background:#3A2410;border:6px solid {INK};'
                 f'transform:scaleX({start});transform-origin:50% 50%">'
                 f'<div style="position:absolute;left:8%;right:8%;top:22%;bottom:10%">{contents[i]}</div>'
                 f'<div id="{{sid}}-alt{n}" style="position:absolute;left:8%;right:8%;top:22%;bottom:10%;opacity:0;background:#3A2410"></div></div>')
        html += (f'<div id="{{sid}}-x{n}" style="position:absolute;left:{x + w * 0.1:.0f}px;top:{y + h * 0.15:.0f}px;width:{w * 0.8:.0f}px;height:{h * 0.75:.0f}px;opacity:0">'
                 f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%"><path d="M12 12 L88 88 M88 12 L12 88" stroke="#C8342B" stroke-width="13" stroke-linecap="round"/></svg></div>')
        if labels:
            col = (label_colors or ["#FFFFFF"] * len(labels))[i]
            fg = INK if col == "#FFFFFF" else "#fff"
            html += (f'<div style="position:absolute;left:{x - 20:.0f}px;width:{w + 40:.0f}px;top:{y + h + 12:.0f}px;text-align:center">'
                     f'<span style="display:inline-block;background:{col};color:{fg};border:5px solid {INK};border-radius:14px;font-weight:900;'
                     f'font-size:{30 if len(labels[i]) > 12 else 36}px;line-height:1.1;padding:6px 12px">{labels[i]}</span></div>')
    if numbers:
        for k, (name, sg) in enumerate(sorted((k, v) for k, v in m.get("signs", {}).items() if k.startswith("plaque"))):
            x, y, w, h = frame_rect(sid, sg["box"])
            html += (f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;display:flex;align-items:center;'
                     f'justify-content:center;font-weight:900;font-size:{h * 0.8:.0f}px;color:#5A2E14">{k + 1}</div>')
    for n, t in open_at:
        js.append(f'tl.to("#{{sid}}-room{n}", {{scaleX: 1, duration: 0.5, ease: "power2.out"}}, {t});')
        sfx.append(["whoosh", t])
    for n, t in cross_at:
        js.append(f'tl.fromTo("#{{sid}}-x{n}", {{opacity: 0, scale: 1.6}}, {{opacity: 0.95, scale: 1, duration: 0.25, ease: "back.out(2)"}}, {t});')
        sfx.append(["stamp", t])
    for n, t, alt in swap_at:
        html = html.replace(f'id="{{sid}}-alt{n}" style="', f'id="{{sid}}-alt{n}" style="', 1)
        html = html.replace(f'<div id="{{sid}}-alt{n}" style="position:absolute;left:8%;right:8%;top:22%;bottom:10%;opacity:0;background:#3A2410"></div>',
                            f'<div id="{{sid}}-alt{n}" style="position:absolute;left:8%;right:8%;top:22%;bottom:10%;opacity:0;background:#3A2410">{alt}</div>')
        js.append(f'tl.to("#{{sid}}-alt{n}", {{opacity: 1, duration: 0.3}}, {t});')
    return {"html": html, "js": js, "sfx": sfx}
