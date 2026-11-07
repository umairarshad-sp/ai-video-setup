"""Draw a simple placeholder Foxley as separate puppet layers.

Every layer is a full-size transparent PNG on the same canvas (W x H), so all
parts line up just by stacking them. The real artwork will follow the same
convention, so nothing else in the pipeline changes when it is swapped in.
"""
import json, math, os, sys
from PIL import Image, ImageDraw

W, H = 900, 1300
SS = 2  # supersample for smooth edges

C = {
    "fur": "#E8762B", "fur_dark": "#C85E1A", "cream": "#F5E6CC", "coat": "#1F4E5F",
    "coat_dark": "#173B48", "scarf": "#F2B134", "gold": "#C9A227", "ink": "#2B2B2B",
    "white": "#FFFFFF", "mouth": "#6B1E1E", "tongue": "#E86A6A", "brass": "#B8862B",
    "glass": "#CFE8EF",
}
OUT_W = 10  # outline width


def canvas():
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def s(v):
    """scale coordinates (number, tuple or list of tuples) for supersampling"""
    if isinstance(v, (int, float)):
        return v * SS
    if isinstance(v, tuple):
        return tuple(x * SS for x in v)
    return [s(p) for p in v]


def save(im, path):
    im.resize((W, H), Image.LANCZOS).save(path)


def ell(d, cx, cy, rx, ry, fill, outline=True, width=OUT_W):
    d.ellipse(s((cx - rx, cy - ry, cx + rx, cy + ry)), fill=fill,
              outline=C["ink"] if outline else None, width=s(width) if outline else 0)


def poly(d, pts, fill, outline=True, width=OUT_W):
    d.polygon(s(pts), fill=fill)
    if outline:
        d.line(s(pts + [pts[0]]), fill=C["ink"], width=s(width), joint="curve")


def line(d, pts, width=OUT_W, fill=None):
    d.line(s(pts), fill=fill or C["ink"], width=s(width), joint="curve")


def arc_pts(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def thick_curve(d, pts, width, fill, outline=True):
    """a stroked path with an ink outline (outline drawn first, wider)"""
    if outline:
        d.line(s(pts), fill=C["ink"], width=s(width + 2 * OUT_W), joint="curve")
        for p in (pts[0], pts[-1]):
            r = (width + 2 * OUT_W) / 2
            d.ellipse(s((p[0] - r, p[1] - r, p[0] + r, p[1] + r)), fill=C["ink"])
    d.line(s(pts), fill=fill, width=s(width), joint="curve")
    for p in (pts[0], pts[-1]):
        r = width / 2
        d.ellipse(s((p[0] - r, p[1] - r, p[0] + r, p[1] + r)), fill=fill)


HEAD = (450, 470)
EYE_L, EYE_R = (372, 455), (528, 455)
MOUTH = (450, 618)


def draw_tail(path):
    im, d = canvas()
    # bushy tail rising behind the body on the right, curling into a "?" hook
    spine = [(560, 1150), (650, 1120), (730, 1040), (760, 940), (745, 840)]
    thick_curve(d, spine, 110, C["fur"])
    hook = arc_pts(700, 800, 60, 60, 20, -200, 30)  # the question-mark curl
    thick_curve(d, [spine[-1]] + hook, 70, C["cream"])
    save(im, path)


def draw_body(path):
    im, d = canvas()
    # feet
    ell(d, 385, 1215, 70, 38, C["fur_dark"])
    ell(d, 515, 1215, 70, 38, C["fur_dark"])
    # coat (trapezoid with rounded hem)
    coat = [(330, 700), (570, 700), (650, 1190), (250, 1190)]
    poly(d, coat, C["coat"])
    # coat opening / chest
    poly(d, [(420, 720), (480, 720), (500, 1000), (450, 1060), (400, 1000)], C["cream"], width=7)
    line(d, [(450, 1060), (450, 1185)], width=7)
    # buttons
    for y in (1090, 1140):
        ell(d, 480, y, 11, 11, C["gold"], width=5)
    # pockets
    line(d, [(300, 1060), (380, 1060)], width=7)
    line(d, [(520, 1060), (600, 1060)], width=7)
    # scarf
    d.rounded_rectangle(s((300, 670, 600, 745)), radius=s(36), fill=C["scarf"], outline=C["ink"], width=s(OUT_W))
    poly(d, [(520, 730), (585, 730), (600, 900), (540, 890)], C["scarf"])
    line(d, [(548, 870), (592, 876)], width=6)
    save(im, path)


def draw_head(path):
    im, d = canvas()
    cx, cy = HEAD
    # ears
    for sgn in (-1, 1):
        ex = cx + sgn * 165
        poly(d, [(ex - 85 * sgn, 330), (ex + 40 * sgn, 175), (ex + 55 * sgn, 380)], C["fur"])
        poly(d, [(ex - 45 * sgn, 330), (ex + 30 * sgn, 230), (ex + 35 * sgn, 360)], C["cream"], outline=False)
    # cheek tufts + head
    poly(d, [(220, 520), (175, 600), (265, 580)], C["fur"])
    poly(d, [(680, 520), (725, 600), (635, 580)], C["fur"])
    ell(d, cx, cy, 240, 205, C["fur"])
    # muzzle
    ell(d, cx, 585, 150, 105, C["cream"], width=8)
    # nose
    ell(d, cx, 548, 32, 22, C["ink"], outline=False)
    ell(d, cx - 9, 541, 9, 5, "#5a5a5a", outline=False)
    save(im, path)


def draw_glasses(path):
    im, d = canvas()
    for (x, y) in (EYE_L, EYE_R):
        d.ellipse(s((x - 66, y - 62, x + 66, y + 62)), outline=C["gold"], width=s(11))
    line(d, [(EYE_L[0] + 64, 445), (450, 432), (EYE_R[0] - 64, 445)], width=9, fill=C["gold"])
    save(im, path)


def eye_white(d, x, y, rx=40, ry=46):
    ell(d, x, y, rx, ry, C["white"], width=7)


def draw_eyes(variant, path):
    im, d = canvas()
    for i, (x, y) in enumerate((EYE_L, EYE_R)):
        v = variant
        if variant == "wink":
            v = "open" if i == 0 else "closed"
        if v == "open":
            eye_white(d, x, y)
            ell(d, x + 4, y + 6, 20, 24, C["ink"], outline=False)
            ell(d, x + 10, y - 2, 7, 7, C["white"], outline=False)
        elif v == "up":
            eye_white(d, x, y)
            ell(d, x + 12, y - 18, 18, 20, C["ink"], outline=False)
            ell(d, x + 17, y - 24, 6, 6, C["white"], outline=False)
        elif v == "halflid":
            eye_white(d, x, y)
            ell(d, x + 4, y + 10, 20, 22, C["ink"], outline=False)
            d.chord(s((x - 42, y - 48, x + 42, y + 48)), 180, 360, fill=C["fur"], outline=C["ink"], width=s(7))
            line(d, [(x - 42, y), (x + 42, y)], width=8)
        elif v == "shocked":
            eye_white(d, x, y, 46, 54)
            ell(d, x, y, 10, 12, C["ink"], outline=False)
        elif v == "closed":
            line(d, arc_pts(x, y - 4, 36, 18, 15, 165), width=9)
        elif v == "happy":
            line(d, arc_pts(x, y + 12, 36, 30, 200, 340), width=10)
    save(im, path)


def draw_brows(variant, path):
    im, d = canvas()
    for i, (x, y) in enumerate((EYE_L, EYE_R)):
        sgn = -1 if i == 0 else 1
        yb = y - 88
        if variant == "neutral":
            pts = [(x - 38, yb + 4), (x + 38, yb - 4)] if sgn < 0 else [(x - 38, yb - 4), (x + 38, yb + 4)]
        elif variant == "raised":
            pts = arc_pts(x, yb - 2, 40, 18, 200, 340, 10)
        elif variant == "smug":  # left down, right up
            pts = [(x - 38, yb + 10), (x + 38, yb + 2)] if sgn < 0 else arc_pts(x, yb - 6, 40, 20, 200, 340, 10)
        elif variant == "frown":
            pts = [(x - 38, yb - 6), (x + 38, yb + 12)] if sgn < 0 else [(x - 38, yb + 12), (x + 38, yb - 6)]
        line(d, pts, width=14, fill=C["fur_dark"])
    save(im, path)


def draw_mouth(shape, path):
    im, d = canvas()
    x, y = MOUTH
    if shape == "X":  # rest: small smile
        line(d, arc_pts(x, y - 20, 42, 22, 20, 160), width=8)
    elif shape == "smirk":
        line(d, [(x - 40, y), (x, y + 4), (x + 30, y - 6), (x + 46, y - 18)], width=8)
    elif shape == "A":  # M B P, closed lips
        line(d, [(x - 38, y), (x + 38, y)], width=9)
    elif shape == "B":  # most consonants, slightly open
        ell(d, x, y, 34, 13, C["mouth"], width=7)
    elif shape == "C":  # E / I, wide open
        ell(d, x, y + 4, 46, 24, C["mouth"], width=7)
        d.rectangle(s((x - 30, y - 18, x + 30, y - 10)), fill=C["white"])
    elif shape == "D":  # A, big open
        ell(d, x, y + 12, 46, 42, C["mouth"], width=7)
        ell(d, x, y + 34, 26, 14, C["tongue"], outline=False)
    elif shape == "E":  # O, round
        ell(d, x, y + 8, 26, 32, C["mouth"], width=7)
    elif shape == "F":  # U / W, pucker
        ell(d, x, y + 4, 15, 17, C["mouth"], width=7)
    elif shape == "G":  # F / V, teeth on lip
        ell(d, x, y + 4, 36, 16, C["mouth"], width=7)
        d.rectangle(s((x - 24, y - 10, x + 24, y + 2)), fill=C["white"])
    save(im, path)


def magnifier(d, cx, cy):
    thick_curve(d, [(cx + 40, cy + 40), (cx + 100, cy + 100)], 22, C["brass"])
    ell(d, cx, cy, 62, 62, C["glass"], width=12)
    d.ellipse(s((cx - 62, cy - 62, cx + 62, cy + 62)), outline=C["brass"], width=s(10))


def draw_arm(variant, path):
    """the right-hand arm (viewer's right). The left arm is static in arm_left.png"""
    im, d = canvas()
    if variant == "left":
        thick_curve(d, [(340, 760), (285, 900), (275, 1010)], 64, C["coat"])
        ell(d, 275, 1040, 40, 36, C["fur"])
    elif variant == "rest":
        thick_curve(d, [(560, 760), (615, 900), (625, 1010)], 64, C["coat"])
        ell(d, 625, 1040, 40, 36, C["fur"])
    elif variant == "point":
        thick_curve(d, [(560, 760), (680, 760), (760, 650)], 64, C["coat"])
        ell(d, 780, 615, 40, 36, C["fur"])
        thick_curve(d, [(790, 595), (820, 545)], 20, C["fur"])
    elif variant == "chin":
        thick_curve(d, [(560, 760), (640, 860), (560, 700)], 64, C["coat"])
        ell(d, 540, 670, 42, 38, C["fur"])
    elif variant == "magnify":
        thick_curve(d, [(560, 760), (690, 800), (730, 700)], 64, C["coat"])
        magnifier(d, 690, 600)
        ell(d, 790, 700, 40, 36, C["fur"])
    elif variant == "facepalm":
        thick_curve(d, [(560, 760), (640, 720), (560, 520)], 64, C["coat"])
        ell(d, 520, 470, 70, 60, C["fur"])
    save(im, path)


def main(out):
    os.makedirs(out, exist_ok=True)
    draw_tail(f"{out}/tail.png")
    draw_body(f"{out}/body.png")
    draw_arm("left", f"{out}/arm_left.png")
    draw_head(f"{out}/head.png")
    draw_glasses(f"{out}/glasses.png")
    for v in ["open", "closed", "up", "halflid", "shocked", "happy", "wink"]:
        draw_eyes(v, f"{out}/eyes_{v}.png")
    for v in ["neutral", "raised", "smug", "frown"]:
        draw_brows(v, f"{out}/brows_{v}.png")
    for m in ["X", "smirk", "A", "B", "C", "D", "E", "F", "G"]:
        draw_mouth(m, f"{out}/mouth_{m}.png")
    for a in ["rest", "point", "chin", "magnify", "facepalm"]:
        draw_arm(a, f"{out}/arm_{a}.png")
    print("placeholder puppet written to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "puppet/placeholder")
