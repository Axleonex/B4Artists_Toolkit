"""Draw the Basic Humanoid asset thumbnail (dev-only; needs Pillow).

Usage: python scripts/make_quick_rig_preview.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets_src", "basic_humanoid_preview.png")

im = Image.new("RGBA", (256, 256), (46, 52, 64, 255))
d = ImageDraw.Draw(im)
orange = (255, 170, 60, 255)
cx = 128
d.ellipse((cx - 16, 40, cx + 16, 72), outline=orange, width=5)
for a, b in [((cx, 72), (cx, 140)), ((cx, 90), (cx - 40, 125)), ((cx, 90), (cx + 40, 125)),
             ((cx, 140), (cx - 28, 190)), ((cx, 140), (cx + 28, 190))]:
    d.line((a, b), fill=orange, width=7)
bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
d.text((cx, 205), "Humanoid", font=bold, fill="white", anchor="mm")
d.text((cx, 232), "19 bones", font=small, fill=(200, 200, 200, 255), anchor="mm")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
im.save(OUT)
print("WROTE", OUT)
