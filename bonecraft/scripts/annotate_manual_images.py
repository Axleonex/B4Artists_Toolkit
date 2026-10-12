"""Turn raw manual screenshots into the chapter's images: crop, scale, red circles / boxes and number badges.

Usage (from bonecraft/):
    python scripts/annotate_manual_images.py docs/manual/images/crescent-rose/circles.json \
        G:/LapArt/output/crescent-rose-captures docs/manual/images/crescent-rose [en ja ...]

circles.json: {"<lang>": {"<image name>": {"crop": [l, t, r, b], "width": W, "marks": [...]}}}.  Marks are in
raw-capture pixels: {"shape": "circle", "center": [x, y], "radius": r, "badge": n} or {"shape": "box",
"box": [l, t, r, b], "badge": n}.  Raw captures stay untouched; rerun this after a UI change or a redraw.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RED = (229, 57, 53)              # #E53935
LINE = 3
BADGE_R = 12
MAX_BYTES = 300 * 1024           # the manual check's limit per image


def _font(size):
    for name in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def annotate(raw_png, out_png, spec):
    raw_png, out_png = Path(raw_png), Path(out_png)
    if not raw_png.exists():
        raise FileNotFoundError(str(raw_png))
    im = Image.open(raw_png).convert("RGB")
    l, t, r, b = spec["crop"]
    im = im.crop((l, t, r, b))
    scale = spec["width"] / im.width
    im = im.resize((spec["width"], round(im.height * scale)), Image.LANCZOS)
    draw = ImageDraw.Draw(im)
    font = _font(16)
    for mark in spec.get("marks", []):
        if mark["shape"] == "circle":
            cx, cy = (mark["center"][0] - l) * scale, (mark["center"][1] - t) * scale
            rad = mark["radius"] * scale
            draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=RED, width=LINE)
            # the badge touches the ring from outside at its top-right, so it never covers the control
            bx, by = cx + (rad + BADGE_R) * 0.7071, cy - (rad + BADGE_R) * 0.7071
        else:
            x0, y0, x1, y1 = mark["box"]
            x0, y0, x1, y1 = (x0 - l) * scale, (y0 - t) * scale, (x1 - l) * scale, (y1 - t) * scale
            draw.rectangle((x0, y0, x1, y1), outline=RED, width=LINE)
            bx, by = x1, y0
        if "badge" in mark:
            draw.ellipse((bx - BADGE_R, by - BADGE_R, bx + BADGE_R, by + BADGE_R), fill=RED)
            draw.text((bx, by), str(mark["badge"]), fill=(255, 255, 255), font=font, anchor="mm")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_png, optimize=True)
    if out_png.stat().st_size > MAX_BYTES:        # a viewport full of textures: a 256-colour palette halves it
        im.quantize(256, dither=Image.Dither.FLOYDSTEINBERG).save(out_png, optimize=True)


def main(argv):
    table = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    captures, images = Path(argv[1]), Path(argv[2])
    langs = argv[3:] or sorted(table)
    for lang in langs:
        for name, spec in table[lang].items():
            annotate(captures / lang / f"{name}.png", images / lang / f"{name}.png", spec)
            print("wrote", lang, name)


if __name__ == "__main__":
    main(sys.argv[1:])
