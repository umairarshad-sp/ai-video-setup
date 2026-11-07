"""Cut the ChatGPT Foxley sheets into a puppet kit (puppet/foxley/).

Talking  = the front-facing bust from the mouth sheet ("Rest" head) with
           mouth patches from the other 7 heads swapped in, plus a drawn blink.
Reacting = the 8 poses from the expression sheet, scaled so the head matches
           the talking bust, bottom-aligned on the same canvas.
"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
OUT = os.path.join(ROOT, "puppet", "foxley")

# ---- mouth sheet geometry (measured)
M_COLS = [(27, 363), (412, 747), (796, 1131), (1180, 1515)]
M_ROWS = [(29, 420), (532, 923)]
M_NAMES = ["MBP", "AI", "E", "O", "U", "FV", "L", "Rest"]
MOUTH_C, MOUTH_R = (166, 255), (54, 29)          # patch ellipse, cell-relative
EYES = [((102, 186), (34, 35)), ((226, 186), (35, 35))]

# ---- expression sheet: pose order, row-major
POSES = ["excited", "proud", "thinking", "shocked", "laugh", "facepalm", "wink", "smug"]

CANVAS = (1000, 900)   # all puppet layers share this canvas
SS = 2                # work at 2x for the mouth sheet (it is low-res)


def remove_white(img, thresh=232):
    """flood-fill the white background from the borders -> RGBA with soft edges"""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    mn = a.min(axis=2)
    sat = a.max(axis=2) - mn
    whiteish = (mn > thresh) & (sat < 25)
    lab, _ = ndi.label(whiteish)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # soft edge: pixels near the background get alpha from how non-white they are
    near = ndi.binary_dilation(bg, iterations=2) & ~bg
    alpha = np.where(bg, 0.0, 1.0)
    soft = np.clip((255 - mn) / (255 - 170), 0, 1)
    alpha = np.where(near, np.minimum(alpha, soft), alpha)
    # un-mix the white from edge colours
    al = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.clip((a - 255 * (1 - al)) / al, 0, 255)
    rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def gold_width(rgba):
    a = np.asarray(rgba).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    gold = (r > 190) & (g > 140) & (g < 215) & (b < 90) & (al > 200) & (r - b > 120)
    ys, xs = np.nonzero(gold)
    # glasses are in the upper half of the figure; ignore the magnifier rim by taking the
    # densest horizontal band of gold
    hist = np.bincount(ys, minlength=a.shape[0])
    band = np.convolve(hist, np.ones(40), "same")
    yc = int(np.argmax(band))
    sel = np.abs(ys - yc) < 30
    xs = xs[sel]
    return np.percentile(xs, 99) - np.percentile(xs, 1), yc


def ellipse_mask(size, c, r, feather):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse((c[0] - r[0], c[1] - r[1], c[0] + r[0], c[1] + r[1]), fill=255)
    return m.filter(ImageFilter.GaussianBlur(feather))


def place(layer, scale, anchor_x, canvas=CANVAS):
    """scale a layer and bottom-align it on the shared canvas, centred on anchor_x"""
    w, h = layer.size
    lw, lh = int(w * scale), int(h * scale)
    lay = layer.resize((lw, lh), Image.LANCZOS)
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    x = int(canvas[0] / 2 - anchor_x * scale)
    out.alpha_composite(lay, (max(x, 0), canvas[1] - lh), (max(-x, 0), 0))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.open(os.path.join(SRC, "mouths.png")).convert("RGB")
    cells = {}
    for r, (y0, y1) in enumerate(M_ROWS):
        for c, (x0, x1) in enumerate(M_COLS):
            cells[M_NAMES[r * 4 + c]] = sheet.crop((x0, y0, x0 + 336, y0 + 392))
    base = cells["Rest"]
    cw, ch = base.size

    # ---------- talking bust (2x upscale for crispness, then placed like the poses)
    base_rgba = remove_white(base)
    gw_bust, _ = gold_width(base_rgba)
    bust_scale = 1.0
    target_glasses = gw_bust * bust_scale  # poses are matched to this
    up = lambda im: im.resize((cw * SS, ch * SS), Image.LANCZOS)  # noqa: E731

    talk = up(base_rgba)
    canvas_scale = 1.0 / SS * (471 / cw)  # bust is 471px wide on the canvas
    # store every talking layer at canvas resolution
    def to_canvas(im_2x):
        return place(im_2x, canvas_scale * 1.0, cw * SS / 2)

    to_canvas(talk).save(os.path.join(OUT, "talk.png"))

    # mouth patches
    mapping = {"A": "MBP", "B": "AI", "C": "E", "D": "AI", "E": "O", "F": "U", "G": "E",
               "smirk": "MBP", "X": "Rest", "L": "L"}
    mask = ellipse_mask((cw, ch), MOUTH_C, MOUTH_R, 4)
    for key, src in mapping.items():
        patch = cells[src].convert("RGBA")
        patch.putalpha(mask)
        to_canvas(up(patch)).save(os.path.join(OUT, f"mouth_{key}.png"))

    # blink: paint lids over both eyes and draw a closed lash line
    lids = Image.new("RGBA", (cw * 4, ch * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(lids)
    arr = np.asarray(base)
    fur = tuple(int(v) for v in arr[146, 102]) + (255,)
    lash = (45, 26, 16, 255)
    for (cx, cy), (rx, ry) in EYES:
        q = 4
        d.ellipse(((cx - rx) * q, (cy - ry) * q, (cx + rx) * q, (cy + ry) * q), fill=fur)
        pts = [((cx - rx + 3 + t * (2 * rx - 6) / 20) * q,
                (cy + 4 + 10 * np.sin(np.pi * t / 20)) * q) for t in range(21)]
        d.line(pts, fill=lash, width=6 * q, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse((p[0] - 3 * q, p[1] - 3 * q, p[0] + 3 * q, p[1] + 3 * q), fill=lash)
    lids = lids.resize((cw * SS, ch * SS), Image.LANCZOS)
    to_canvas(lids).save(os.path.join(OUT, "eyes_closed.png"))

    # ---------- reaction poses
    ex = Image.open(os.path.join(SRC, "expressions.png")).convert("RGB")
    ex_rgba = remove_white(ex)
    A = np.asarray(ex_rgba)
    fg = A[..., 3] > 40
    lab, n = ndi.label(fg)
    sizes = ndi.sum(fg, lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    figs = [i + 1 for i, s in enumerate(sizes) if s > 50000]
    figs.sort(key=lambda i: (objs[i - 1][0].start > 510, objs[i - 1][1].start))
    centers = {i: ((objs[i - 1][1].start + objs[i - 1][1].stop) / 2, objs[i - 1][0].start > 510) for i in figs}
    owner = np.zeros(n + 1, dtype=int)
    for i in range(1, n + 1):
        if sizes[i - 1] < 150:
            continue
        o = objs[i - 1]
        cx, row2 = (o[1].start + o[1].stop) / 2, o[0].start > 510
        if i in figs:
            owner[i] = i
        else:
            cands = [f for f in figs if centers[f][1] == row2]
            owner[i] = min(cands, key=lambda f: abs(centers[f][0] - cx))
    # Match head size with the ear-to-ear width just below the ear tips, then line the
    # pose's ear tips up with the talking head's so the head stays put when cutting
    # between talking and reacting. The pose's waist runs past the canvas bottom,
    # where the desk in the video hides it anyway.
    def head_band(alpha, top):
        band = alpha[top + 30: top + 110] > 128
        xs = np.nonzero(band.any(axis=0))[0]
        return xs.max() - xs.min(), (xs.max() + xs.min()) / 2

    talk_a = np.asarray(Image.open(os.path.join(OUT, "talk.png")))[..., 3]
    talk_top = int(np.nonzero((talk_a > 128).any(axis=1))[0][0])
    talk_span, talk_cx = head_band(talk_a, talk_top)
    talk_cx = CANVAS[0] / 2

    figs_rgba, spans = {}, []
    for name, f in zip(POSES, figs):
        keep = owner[lab] == f
        rgba = A.copy()
        rgba[..., 3] = np.where(keep, rgba[..., 3], 0)
        main_a = np.where(lab == f, A[..., 3], 0)          # main figure only (no effects)
        ftop = int(np.nonzero((main_a > 128).any(axis=1))[0][0])
        span, hcx = head_band(main_a, ftop)
        figs_rgba[name] = (rgba, ftop, hcx)
        spans.append(span)
    scale = talk_span / float(np.median(spans))           # one scale: the sheet is drawn consistently
    print(f"pose scale {scale:.3f} (talk ear span {talk_span}px, pose median {np.median(spans):.0f}px)")
    for name, (rgba, ftop, hcx) in figs_rgba.items():
        ys, xs = np.nonzero(rgba[..., 3] > 0)
        x0, y0 = xs.min(), ys.min()
        crop = Image.fromarray(rgba).crop((x0, y0, xs.max() + 1, ys.max() + 1))
        lay = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
        out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        px = int(talk_cx - (hcx - x0) * scale)
        py = int(talk_top - (ftop - y0) * scale)
        out.alpha_composite(lay, (max(px, 0), max(py, 0)), (max(-px, 0), max(-py, 0)))
        out.save(os.path.join(OUT, f"pose_{name}.png"))

    rig = {
        "name": "Foxley",
        "kind": "bust",
        "display": {"left": -10, "top": 670, "scale": 1.1},
        "desk": True,
        "canvas": list(CANVAS),
        "layers": [
            {"slot": "body", "group": "body", "files": {"talk": "talk.png", **{f"pose_{p}": f"pose_{p}.png" for p in POSES}}},
            {"slot": "mouth", "group": "body", "files": {k: f"mouth_{k}.png" for k in mapping}},
            {"slot": "eyes", "group": "body", "files": {"closed": "eyes_closed.png"}},
        ],
        "expressions": {
            "neutral": None, "smug": "pose_smug", "proud": "pose_proud", "thinking": "pose_thinking",
            "shocked": "pose_shocked", "laugh": "pose_laugh", "point": "pose_laugh", "excited": "pose_excited",
            "facepalm": "pose_facepalm", "wink": "pose_wink",
        },
    }
    json.dump(rig, open(os.path.join(OUT, "rig.json"), "w"), indent=2)
    print("puppet written to", OUT)


if __name__ == "__main__":
    main()
