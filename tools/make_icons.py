"""App icon from the poster: full-width square around the logo; the gear badge is removed by
mirroring the clean sky from the opposite corner (a flat fill showed as a dark block)."""
from PIL import Image, ImageOps
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC = os.path.join(ROOT, "assets", "ui", "cover.png")
ICONS = os.path.join(ROOT, "assets", "icons")

im = Image.open(SRC).convert("RGB")
W, H = im.size

side = W
left = 0
top = int(H * 0.055)
crop = im.crop((left, top, left + side, top + side)).copy()

badge = int(side * 0.20)
patch = crop.crop((0, 0, badge, badge)).transpose(Image.FLIP_LEFT_RIGHT)
crop.paste(patch, (side - badge, 0))

for s in (1024, 180, 167, 152, 120, 87, 80, 76, 60, 58, 40, 29, 20):
    crop.resize((s, s), Image.LANCZOS).save(os.path.join(ICONS, "icon-%d.png" % s), optimize=True)

crop.resize((1024, 1024), Image.LANCZOS).save(os.path.join(ICONS, "icon-1024.png"), optimize=True)
print("icons rebuilt with a mirrored sky patch")
