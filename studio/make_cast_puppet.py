"""Cut a character's ChatGPT acting sheet into a puppet for story scenes.

    .venv/bin/python studio/make_cast_puppet.py <id> [<id> ...]     # or: all

Reads cast/<id>/art/acting.png and cast/<id>/profile.json, writes puppet/cast/<id>/:
  pose_<name>.png   every pose, cut out, on one shared canvas, feet on its bottom edge
  mouth_*.png       talking mouths for the neutral pose, on the same canvas
  rig.json          canvas size, figure height, poses, mouth layers
and a preview sheet work/puppet_<id>.png.

Mouths: by default the open mouth is lifted from pose 2 (same pose, mouth open) after
lining pose 2 up with pose 1; the mouth area is found where the two drawings differ most
below the eyes. If profile.json sets art.mouth.method to "draw" (Barnaby), mouths are drawn
along the closed smile instead.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "studio"))
from make_foxley_puppet import remove_white  # noqa: E402

PAD = 24


def sheet_rows(a):
    fg = a.min(axis=2) < 225
    rows = np.nonzero(fg.any(axis=1))[0]
    return max(rows[0] - 10, 0), min(rows[-1] + 10, a.shape[0])


def clean_figure(rgba):
    """keep the main figure and its small effects (sweat drops, steam); drop slivers of
    neighbouring poses that touch the left or right edge of the crop"""
    al = rgba[..., 3] > 40
    lab, n = ndi.label(al)
    if n == 0:
        return rgba
    sizes = ndi.sum(al, lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    objs = ndi.find_objects(lab)
    keep = np.zeros(n + 1, bool)
    keep[main] = True
    W = rgba.shape[1]
    for i in range(1, n + 1):
        if i == main or sizes[i - 1] < 40:
            continue
        o = objs[i - 1]
        touches_edge = o[1].start <= 1 or o[1].stop >= W - 1
        if not touches_edge:
            keep[i] = True
    out = rgba.copy()
    out[..., 3] = np.where(keep[lab], out[..., 3], 0)
    return out


def clear_enclosed_white(rgba, head_frac=0.36, min_size=8):
    """Remove background white that survived the edge flood-fill in remove_white.

    1. Defringe: light, unsaturated pixels touching transparency (white halos around curls,
       hands and other edges) are made transparent.
    2. Enclosed white: pure-white patches fenced in by the black outline (>= 80% of a thin
       ring around them is ink): gaps between an arm and the body, between close legs, behind
       a cane, between curls. Costume white (sneakers, lens glare, eye whites) borders coloured
       shading and is kept. In the head only the sides (hair) are cleared, never the face,
       since pupil highlights and teeth are ringed by dark too. Cleared patches grow into their
       light anti-aliased rims.
    Returns the cleaned image and the number of enclosed patches cleared."""
    out = rgba.copy()
    rgb = out[..., :3].astype(int)
    mn, sat = rgb.min(axis=2), rgb.max(axis=2) - rgb.min(axis=2)
    light = (mn > 215) & (sat < 28)
    # 1. defringe: flood from the transparent outside through every light pixel it can reach
    #    (halos, and white notches between curls at the silhouette's edge)
    clear = out[..., 3] < 40
    lab, _ = ndi.label(clear | light)
    outside = np.unique(lab[clear])
    reach = np.isin(lab, outside[outside > 0]) & ~clear
    # only near the silhouette edge, so a light area without an outline (Rafiq's chef hat at
    # the sheet's top edge) is never eaten; halos and curl notches are within a few pixels
    near = ndi.distance_transform_edt(~clear) <= 7
    out[..., 3] = np.where(reach & near, 0, out[..., 3])
    al = out[..., 3]
    ys = np.nonzero((al > 128).any(axis=1))[0]
    if not len(ys):
        return out, 0
    top, bot = ys[0], ys[-1]
    head_line = top + head_frac * (bot - top)
    core = (al > 120) & (mn > 243) & (sat < 14)
    lab, n = ndi.label(core)
    # the face: middle of the head's width, where eyes, highlights and teeth are
    head_cols = np.nonzero((al[top:int(head_line)] > 128).any(axis=0))[0]
    hx0, hx1 = head_cols.min(), head_cols.max()
    face_lo, face_hi = hx0 + 0.22 * (hx1 - hx0), hx1 - 0.22 * (hx1 - hx0)
    ink = mn < 90
    cleared = np.zeros(al.shape, bool)
    count = 0
    for i, o in enumerate(ndi.find_objects(lab)):
        m = np.zeros(al.shape, bool)
        m[o] = lab[o] == i + 1
        if m.sum() < min_size:
            continue
        # background showing through is fenced in by the black outline; white that belongs to
        # the drawing (sneaker toes, lens glare, eye whites) sits against coloured shading
        ring = ndi.binary_dilation(m, iterations=3) & ~ndi.binary_dilation(m, iterations=1)
        cy, cx = (o[0].start + o[0].stop) / 2, (o[1].start + o[1].stop) / 2
        in_head = cy < head_line
        if in_head and face_lo < cx < face_hi:
            continue  # eye highlights and teeth are also ringed by dark: keep the whole face
        # hair (head sides) is loosely outlined, so a looser ring counts there
        if ink[ring].mean() < (0.55 if in_head else 0.8):
            continue
        cleared |= m
        count += 1
    if count:  # 2b. grow into the light anti-aliased rim of each cleared patch
        soft = (mn > 200) & (sat < 30)
        for _ in range(2):
            cleared |= ndi.binary_dilation(cleared, iterations=1) & soft
        out[..., 3] = np.where(cleared, 0, out[..., 3])
    return out, count


def figure_anchor(rgba):
    """feet bottom and the horizontal centre of the legs (bottom 20% of the figure)"""
    al = rgba[..., 3] > 128
    ys = np.nonzero(al.any(axis=1))[0]
    top, bot = ys[0], ys[-1]
    legs = al[int(bot - 0.2 * (bot - top)):bot + 1]
    xs = np.nonzero(legs.any(axis=0))[0]
    return top, bot, (xs.min() + xs.max()) / 2


def align(p1, p2):
    """offset (dx, dy) that best lines p2 up with p1 on the head region"""
    def head_cx(p):
        band = p[40:320].min(axis=2) < 225
        xs = np.nonzero(band.any(axis=0))[0]
        return (xs.min() + xs.max()) / 2
    s0 = int(round(head_cx(p1) - head_cx(p2)))
    face = slice(40, 320)
    best = min((np.abs(p1[face] - np.roll(np.roll(p2, dy, 0), s0 + dx, 1)[face]).mean(), s0 + dx, dy)
               for dx in range(-25, 26) for dy in range(-12, 13))
    return best[1], best[2], best[0]


def find_mouth(p1, p2s, alpha):
    """centre and radii of the mouth: the biggest changed blob in the lower half of the head"""
    d = np.abs(p1 - p2s).max(axis=2)
    d[alpha < 200] = 0
    ys = np.nonzero((alpha > 200).any(axis=1))[0]
    top = ys[0]
    # the head is roughly the top 40% of a chibi figure; the mouth sits in its lower part
    fig_h = ys[-1] - top
    y0, y1 = int(top + 0.12 * fig_h), int(top + 0.42 * fig_h)
    m = np.zeros_like(d, bool)
    m[y0:y1] = d[y0:y1] > 90
    m = ndi.binary_opening(m, iterations=1)
    m = ndi.binary_closing(m, iterations=3)
    lab, n = ndi.label(m)
    if n == 0:
        raise RuntimeError("no mouth difference found")
    best, score = None, -1
    for i, o in enumerate(ndi.find_objects(lab)):
        area = (lab[o] == i + 1).sum()
        h, w = o[0].stop - o[0].start, o[1].stop - o[1].start
        # mouths are wider than tall and solid; eyes come in pairs high up, outlines are thin
        s = area * (1.0 if w >= h * 0.8 else 0.4) * (1 + (o[0].start - y0) / max(y1 - y0, 1))
        if s > score:
            best, score = o, s
    cy, cx = (best[0].start + best[0].stop) / 2, (best[1].start + best[1].stop) / 2
    ry, rx = (best[0].stop - best[0].start) / 2 + 7, (best[1].stop - best[1].start) / 2 + 9
    return (cx, cy), (rx, ry)


def drawn_mouths(base_rgb, smile, skin, scale=6):
    """Barnaby-style: cover the closed smile with skin and draw open mouths along it"""
    W, H = base_rgb.size
    P0, P1, P2 = smile
    ctrl = (2 * P1[0] - (P0[0] + P2[0]) / 2, 2 * P1[1] - (P0[1] + P2[1]) / 2)

    def bez(p0, c, p2, n=40):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0],
                 (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]
    Q = scale
    S = lambda pts: [(x * Q, y * Q) for x, y in pts]  # noqa: E731
    out = {}
    for name, op, teeth in [("small", 4, False), ("medium", 8, True), ("wide", 13, True)]:
        lay = Image.new("RGBA", (W * Q, H * Q), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        cover = Image.new("L", lay.size, 0)
        ImageDraw.Draw(cover).line(S(bez(P0, ctrl, P2)), fill=255, width=7 * Q)
        lay.paste(Image.new("RGBA", lay.size, tuple(skin) + (255,)), (0, 0), cover.filter(ImageFilter.GaussianBlur(Q * 1.2)))
        upper = bez(P0, ctrl, P2)
        lower = bez(P2, (ctrl[0], ctrl[1] + op * 2), P0)
        shape = upper + lower[1:]
        d.polygon(S(shape), fill=(110, 30, 32, 255))
        sm = Image.new("L", lay.size, 0)
        ImageDraw.Draw(sm).polygon(S(shape), fill=255)
        sm_a = np.asarray(sm)
        if teeth:
            band = Image.new("L", lay.size, 0)
            ImageDraw.Draw(band).line(S([(x, y + 1.6) for x, y in upper]), fill=255, width=int(3.2 * Q))
            lay.paste(Image.new("RGBA", lay.size, (250, 248, 240, 255)), (0, 0),
                      Image.fromarray(np.minimum(sm_a, np.asarray(band))))
        mid = lower[len(lower) // 2]
        tm = Image.new("L", lay.size, 0)
        ImageDraw.Draw(tm).ellipse(((mid[0] - 13) * Q, (mid[1] - op * 0.55) * Q, (mid[0] + 13) * Q, (mid[1] + 3) * Q), fill=255)
        lay.paste(Image.new("RGBA", lay.size, (226, 110, 104, 255)), (0, 0), Image.fromarray(np.minimum(np.asarray(tm), sm_a)))
        d.line(S(shape + [shape[0]]), fill=(42, 24, 18, 255), width=int(2.6 * Q), joint="curve")
        out[name] = lay.resize((W, H), Image.LANCZOS)
    return out


def build(cid):
    prof = json.load(open(os.path.join(ROOT, "cast", cid, "profile.json")))
    art = prof["art"]
    sheet = Image.open(os.path.join(ROOT, "cast", cid, "art", "acting.png")).convert("RGB")
    a = np.asarray(sheet).astype(np.float32)
    chk = json.load(open(os.path.join(ROOT, "cast", cid, "art", "check.json")))
    cols = art.get("pose_columns") or chk["pose_columns"]
    top, bot = sheet_rows(a.astype(int))
    names = art["acting_poses"]
    crops = [a[top:bot, cols[i]:cols[i + 1]] for i in range(len(names))]

    # cut out every pose, with a margin so a cut between touching poses never lands inside a
    # shoe or a hand (the flood-fill would eat into white parts that touch the crop edge);
    # clean_figure then drops the neighbour's slivers
    MARGIN = art.get("pose_margin", 0)  # set per character when poses overlap (Bunty's shoes)
    margins = []
    poses = {}
    for i, name in enumerate(names):
        x0, x1 = max(cols[i] - MARGIN, 0), min(cols[i + 1] + MARGIN, a.shape[1])
        margins.append((cols[i] - x0, x1 - cols[i + 1]))
        c = a[top:bot, x0:x1]
        rgba = np.asarray(remove_white(Image.fromarray(c.astype(np.uint8)))).copy()
        fig = clean_figure(rgba)
        # the margin can pull in pieces of the neighbouring poses: drop any detached piece
        # that reaches the original cut lines (or lies outside this pose's own column)
        L, _ = margins[-1]
        lo, hi = L, L + (cols[i + 1] - cols[i])
        lab, n = ndi.label(fig[..., 3] > 40)
        if n > 1:
            sizes = ndi.sum(fig[..., 3] > 40, lab, range(1, n + 1))
            main = int(np.argmax(sizes)) + 1
            xs_all = np.arange(fig.shape[1])[None, :]
            for j, o in enumerate(ndi.find_objects(lab), 1):
                if j == main:
                    continue
                piece = lab == j
                outside = (piece & ((xs_all < lo) | (xs_all >= hi))).sum() / max(piece.sum(), 1)
                crosses = o[1].start < lo + 8 or o[1].stop > hi - 8
                if crosses or outside > 0.3:
                    fig[..., 3] = np.where(piece, 0, fig[..., 3])
        # sheet x positions where two poses touch exactly on the cut line (Rafiq's hats):
        # clip there so the neighbour's piece is dropped, but only at those boundaries
        L, _ = margins[-1]
        for bx in art.get("clip_at", []):
            if bx == cols[i + 1]:
                fig[:, L + (cols[i + 1] - cols[i]) + 3:, 3] = 0
            elif bx == cols[i]:
                fig[:, :max(L - 3, 0), 3] = 0
        fig, k = clear_enclosed_white(fig, art.get("head_frac", 0.36))
        poses[name] = fig

    # mouths on the neutral pose (pose 1); they are built in the un-widened crop's coordinates
    L0 = margins[0][0]
    alpha0 = poses[names[0]][:, L0:L0 + crops[0].shape[1], 3]
    p1 = crops[0]
    mouth_layers = {}
    mouth_info = {}
    method = art.get("mouth", {}).get("method", "patch")
    if method == "draw":
        m = art["mouth"]
        smile = [(x - cols[0], y - top) for x, y in m["smile"]]
        drawn = drawn_mouths(Image.fromarray(p1.astype(np.uint8)), smile, m["skin"])
        for k, lay in drawn.items():
            arr = np.asarray(lay).copy()
            arr[..., 3] = np.minimum(arr[..., 3], alpha0)
            mouth_layers[k] = arr
        mouth_info = {"method": "draw", "shapes": ["small", "medium", "wide"]}
    else:
        p2 = crops[1]
        w = max(p1.shape[1], p2.shape[1])
        pad = lambda p: np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=255)  # noqa: E731
        P1, P2 = pad(p1), pad(p2)
        dx, dy, score = align(P1, P2)
        if "offset" in art.get("mouth", {}):   # hand-set pose2 -> pose1 offset
            dx, dy = art["mouth"]["offset"]
        P2s = np.roll(np.roll(P2, dy, 0), dx, 1)
        alpha1 = np.pad(alpha0, ((0, 0), (0, w - p1.shape[1])))
        if "center" in art.get("mouth", {}):   # set by hand in sheet coordinates
            cx, cy = art["mouth"]["center"][0] - cols[0], art["mouth"]["center"][1] - top
            rx, ry = art["mouth"]["radius"]
        else:
            (cx, cy), (rx, ry) = find_mouth(P1, P2s, alpha1)
        mask = Image.new("L", (w, P1.shape[0]), 0)
        ImageDraw.Draw(mask).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=255)
        mask = np.asarray(mask.filter(ImageFilter.GaussianBlur(art.get("mouth", {}).get("feather", 3.5)))).astype(np.float32)
        patch = np.dstack([P2s, np.minimum(mask, alpha1)])[:, :p1.shape[1]].astype(np.uint8)
        mouth_layers["open"] = patch
        mouth_info = {"method": "patch", "shapes": ["open"], "center": [round(cx), round(cy)],
                      "radius": [round(rx), round(ry)], "offset": [dx, dy], "match": round(float(score), 1)}

    # shared canvas: feet on the bottom edge, legs centred
    anchors = {k: figure_anchor(v) for k, v in poses.items()}
    half_w = max(max(cx - np.nonzero((v[..., 3] > 40).any(axis=0))[0].min(),
                     np.nonzero((v[..., 3] > 40).any(axis=0))[0].max() - cx)
                 for v, (_, _, cx) in zip(poses.values(), anchors.values()))
    height = max(bt - tp for tp, bt, _ in anchors.values())
    CW, CH = int(2 * half_w + 2 * PAD), int(height + PAD)
    out_dir = os.path.join(ROOT, "puppet", "cast", cid)
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    def place(arr, anchor):
        tp, bt, cx = anchor
        img = Image.fromarray(arr)
        canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        canvas.alpha_composite(img, (int(round(CW / 2 - cx)), int(CH - 1 - bt)))
        return canvas

    for name, arr in poses.items():
        place(arr, anchors[name]).save(os.path.join(out_dir, f"pose_{name}.png"))
    for k, arr in mouth_layers.items():
        arr = np.pad(arr, ((0, 0), margins[0], (0, 0)))  # line up with the widened neutral pose
        place(arr, anchors[names[0]]).save(os.path.join(out_dir, f"mouth_{k}.png"))
    ntop, nbot, _ = anchors[names[0]]
    rig = {"id": cid, "name": prof["name"], "canvas": [CW, CH], "figure_height": int(nbot - ntop),
           "facing": art.get("facing", "front"), "poses": names, "talk_pose": names[0],
           "mouth": mouth_info, "voice": prof.get("voice"), "height": prof["height"]}
    json.dump(rig, open(os.path.join(out_dir, "rig.json"), "w"), indent=2)

    # preview: every pose, plus the neutral pose with each mouth
    tiles = [Image.open(os.path.join(out_dir, f"pose_{n}.png")) for n in names]
    for k in mouth_layers:
        t = Image.open(os.path.join(out_dir, f"pose_{names[0]}.png")).copy()
        t.alpha_composite(Image.open(os.path.join(out_dir, f"mouth_{k}.png")))
        tiles.append(t)
    sheet_out = Image.new("RGB", (CW * len(tiles), CH), "#E9D8B8")
    for i, t in enumerate(tiles):
        sheet_out.paste(t, (i * CW, 0), t)
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    sheet_out.save(os.path.join(ROOT, "work", f"puppet_{cid}.png"))
    print(f"{cid}: canvas {CW}x{CH}, figure {rig['figure_height']}px, mouth {mouth_info}")


if __name__ == "__main__":
    ids = sys.argv[1:]
    if ids == ["all"]:
        ids = sorted(d for d in os.listdir(os.path.join(ROOT, "cast"))
                     if os.path.exists(os.path.join(ROOT, "cast", d, "art", "acting.png")))
    for cid in ids:
        build(cid)
