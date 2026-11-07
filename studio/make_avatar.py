"""Profile pictures for @AskFoxley, made from Foxley's own art (source/fullbody.png).

    .venv/bin/python studio/make_avatar.py

Writes branding/avatar_<style>.png (1080x1080, safe for a circular crop) and
work/avatar_preview.png (each one masked to a circle at full size and at feed size).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "studio"))
from make_foxley_puppet import remove_white  # noqa: E402

S = 1080
TEAL, TEAL_DARK, MUSTARD, ORANGE, CREAM, INK = "#1F4E5F", "#163844", "#F2B134", "#E8762B", "#FFF4E0", "#2B2B2B"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def radial(c_in, c_out, centre=(0.5, 0.42)):
    y, x = np.mgrid[0:S, 0:S] / S
    d = np.clip(np.hypot(x - centre[0], y - centre[1]) / 0.72, 0, 1)[..., None]
    a, b = np.array(hexrgb(c_in), float), np.array(hexrgb(c_out), float)
    return Image.fromarray((a * (1 - d) + b * d).astype(np.uint8), "RGB").convert("RGBA")


def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def question_marks(img, colour, alpha):
    d = ImageDraw.Draw(img)
    for x, y, s, r in [(120, 170, 170, -14), (880, 140, 140, 12), (90, 640, 120, 10), (930, 600, 160, -10),
                       (250, 900, 110, 16), (820, 900, 120, -18)]:
        layer = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((s * 0.45, s * 0.1), "?", font=font(s), fill=hexrgb(colour) + (alpha,))
        layer = layer.rotate(r, resample=Image.BICUBIC)
        img.alpha_composite(layer, (int(x - s), int(y - s)))


def cut_foxley():
    full = Image.open(os.path.join(ROOT, "source", "fullbody.png")).convert("RGB")
    fox = remove_white(full)
    # head, scarf and raised magnifier; the coat below is cut by the circle anyway
    a = np.asarray(fox).copy()
    a[410:, 800:, 3] = 0       # the tail, to the right of the coat and below the head
    return Image.fromarray(a).crop((30, 40, 880, 900))


def compose(style):
    if style == "teal":
        bg = radial("#2E6E82", TEAL_DARK)
        question_marks(bg, "#FFFFFF", 28)
    elif style == "sunny":
        bg = radial("#FFD36B", ORANGE)
        question_marks(bg, "#FFFFFF", 45)
    else:  # study: Foxley's own study background, softened
        st = Image.open(os.path.join(ROOT, "source", "background.png")).convert("RGB")
        w, h = st.size
        st = st.crop((0, int(h * 0.22), w, int(h * 0.22) + w)).resize((S, S), Image.LANCZOS)
        bg = st.filter(ImageFilter.GaussianBlur(6)).convert("RGBA")
        bg.alpha_composite(Image.new("RGBA", (S, S), hexrgb(TEAL) + (90,)))
    fox = cut_foxley()
    k = 930 / fox.height                       # head fully inside the ring, chest cut by the circle
    fox = fox.resize((int(fox.width * k), int(fox.height * k)), Image.LANCZOS)
    # soft shadow for depth
    sh = Image.new("RGBA", fox.size, (0, 0, 0, 0))
    sh.putalpha(fox.split()[3].point(lambda v: int(v * 0.35)))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    x, y = (S - fox.width) // 2 + 10, 118
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.alpha_composite(sh, (x + 10, y + 16))
    layer.alpha_composite(fox, (x, y))
    inside = Image.new("L", (S * 2, S * 2), 0)
    ImageDraw.Draw(inside).ellipse((90, 90, S * 2 - 90, S * 2 - 90), fill=255)
    inside = inside.resize((S, S), Image.LANCZOS)
    layer.putalpha(Image.fromarray(np.minimum(np.asarray(layer.split()[3]), np.asarray(inside))))
    bg.alpha_composite(layer)
    # a mustard ring just inside the circle crop, like a badge
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ring)
    d.ellipse((22, 22, S - 22, S - 22), outline=hexrgb(INK) + (255,), width=34)
    d.ellipse((28, 28, S - 28, S - 28), outline=hexrgb(MUSTARD) + (255,), width=22)
    bg.alpha_composite(ring)
    return bg.convert("RGB")


def circle(img, size):
    im = img.resize((size, size), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * 4, size * 4), fill=255)
    im.putalpha(m.resize((size, size), Image.LANCZOS))
    return im


def main():
    out_dir = os.path.join(ROOT, "branding")
    os.makedirs(out_dir, exist_ok=True)
    styles = ["teal", "sunny", "study"]
    imgs = {}
    for s in styles:
        imgs[s] = compose(s)
        imgs[s].save(os.path.join(out_dir, f"avatar_{s}.png"))
    # preview: big circle + feed-size circle (110 px) for each style
    pv = Image.new("RGBA", (len(styles) * 560, 700), (250, 250, 250, 255))
    d = ImageDraw.Draw(pv)
    for i, s in enumerate(styles):
        pv.alpha_composite(circle(imgs[s], 500), (i * 560 + 30, 20))
        pv.alpha_composite(circle(imgs[s], 110), (i * 560 + 225, 560))
        d.text((i * 560 + 30, 530), f"{s}  (below: actual feed size)", fill=(60, 60, 60), font=font(22))
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    pv.convert("RGB").save(os.path.join(ROOT, "work", "avatar_preview.png"))
    print("wrote", ", ".join(f"branding/avatar_{s}.png" for s in styles))


if __name__ == "__main__":
    main()
