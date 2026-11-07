"""Import a cast member's ChatGPT sheets and check them for the puppet.

    .venv/bin/python studio/check_cast_art.py <id> <turnaround image> <acting image>

Saves the sheets as cast/<id>/art/turnaround.png and acting.png, finds the 6 poses on
the acting sheet (by connected shapes, or by the emptiest columns when poses touch),
lines pose 2 (mouth open) up with pose 1 (mouth closed) and writes a comparison strip to
work/<id>_p1p2.png: pose 1 | pose 2 aligned | difference. A dark face with a bright mouth
in the difference means pose 2's mouth can be patched onto pose 1.
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pose_columns(a, n_poses=6):
    fg = a.min(axis=2) < 225
    lab, n = ndi.label(ndi.binary_closing(fg, iterations=3))
    sizes = ndi.sum(fg, lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    figs = sorted((objs[i][1].start, objs[i][1].stop) for i, s in enumerate(sizes) if s > 20000)
    if len(figs) == n_poses:
        cols = [0] + [(figs[i][1] + figs[i + 1][0]) // 2 for i in range(n_poses - 1)] + [a.shape[1]]
        return cols, "shapes"
    col = fg.sum(axis=0)
    w = a.shape[1]
    cuts = []
    for k in range(1, n_poses):
        c = int(k * w / n_poses)
        lo, hi = c - 60, c + 60
        cuts.append(lo + int(np.argmin(col[lo:hi])))
    return [0] + cuts + [w], "column gaps"


def main():
    cid, turn, act = sys.argv[1:4]
    art = os.path.join(ROOT, "cast", cid, "art")
    os.makedirs(art, exist_ok=True)
    Image.open(turn).convert("RGB").save(os.path.join(art, "turnaround.png"))
    im = Image.open(act).convert("RGB")
    im.save(os.path.join(art, "acting.png"))
    a = np.asarray(im).astype(int)
    cols, how = pose_columns(a)
    print(f"acting sheet {im.size}, poses split by {how}: columns {cols}")
    fg = a.min(axis=2) < 225
    rows = np.nonzero(fg.any(axis=1))[0]
    top, bot = max(rows[0] - 10, 0), min(rows[-1] + 10, a.shape[0])
    p1 = a[top:bot, cols[0]:cols[1]].astype(float)
    p2 = a[top:bot, cols[1]:cols[2]].astype(float)
    w = max(p1.shape[1], p2.shape[1])
    pad = lambda p: np.pad(p, ((0, 0), (0, w - p.shape[1]), (0, 0)), constant_values=255)  # noqa: E731
    p1, p2 = pad(p1), pad(p2)
    # coarse: line up the horizontal centre of each figure's head band, then search finely
    def head_cx(p):
        band = p[40:320].min(axis=2) < 225
        xs = np.nonzero(band.any(axis=0))[0]
        return (xs.min() + xs.max()) / 2
    shift0 = int(round(head_cx(p1) - head_cx(p2)))
    p2 = np.roll(p2, shift0, 1)
    face = slice(40, 320)  # head region, where alignment matters
    best = min((np.abs(p1[face] - np.roll(np.roll(p2, dy, 0), dx, 1)[face]).mean(), dx, dy)
               for dx in range(-25, 26) for dy in range(-12, 13))
    score, dx, dy = best
    dx += shift0
    print(f"pose 2 -> pose 1 offset ({dx}, {dy}), mean difference {score:.1f} "
          "(under ~25: patch the real mouth; much higher: draw mouths instead)")
    p2s = np.roll(np.roll(p2, dy, 0), dx - shift0, 1)
    d = np.abs(p1 - p2s).max(axis=2)
    h = min(340, p1.shape[0])
    strip = Image.new("RGB", (w * 3, h), "white")
    strip.paste(Image.fromarray(p1[:h].astype(np.uint8)), (0, 0))
    strip.paste(Image.fromarray(p2s[:h].astype(np.uint8)), (w, 0))
    strip.paste(Image.fromarray(np.clip(d[:h] * 2, 0, 255).astype(np.uint8)).convert("RGB"), (2 * w, 0))
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    out = os.path.join(ROOT, "work", f"{cid}_p1p2.png")
    strip.save(out)
    print("comparison:", out, f"(crop origin x={cols[0]}, y={top})")
    json.dump({"pose_columns": cols, "crop_top": int(top), "pose2_offset": [dx, dy], "match_score": round(score, 1)},
              open(os.path.join(art, "check.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
