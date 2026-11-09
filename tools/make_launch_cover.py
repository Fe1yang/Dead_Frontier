"""Bake the tap prompt into the cover so it can also be used as a static launch image."""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC = os.path.join(ROOT, "assets", "ui", "title_screen.png")
OUT = os.path.join(ROOT, "assets", "ui", "launch_cover.png")

im = Image.open(SRC).convert("RGBA")
W, H = im.size
draw = ImageDraw.Draw(im, "RGBA")

font = None
for cand in (
    os.path.join(ROOT, "assets", "fonts", "NotoSansSC-Bold.otf"),
    os.path.join(ROOT, "assets", "fonts", "NotoSansSC-Regular.otf"),
):
    if os.path.exists(cand):
        font = ImageFont.truetype(cand, int(H * 0.022))
        break
if font is None:
    for name in os.listdir(os.path.join(ROOT, "assets", "fonts")):
        if name.endswith((".otf", ".ttf")):
            font = ImageFont.truetype(os.path.join(ROOT, "assets", "fonts", name), int(H * 0.022))
            break

text = "点击任意处开始"
if font is not None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
else:
    tw, th = W * 0.4, H * 0.02

cx = W // 2
cy = int(H * 0.925)
pad_x, pad_y = int(tw * 0.28), int(th * 0.75)
pill = [cx - tw // 2 - pad_x, cy - th // 2 - pad_y, cx + tw // 2 + pad_x, cy + th // 2 + pad_y]

overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
od.rounded_rectangle(pill, radius=int(th * 0.55), fill=(6, 8, 12, 170), outline=(242, 184, 82, 235), width=max(2, W // 400))
im = Image.alpha_composite(im, overlay)
draw = ImageDraw.Draw(im)
draw.text((cx - tw // 2, cy - th // 2 - bbox[1] if font else cy), text, font=font, fill=(255, 243, 200, 255))

im.convert("RGB").save(OUT, quality=92)
print("launch cover written:", OUT, im.size)
