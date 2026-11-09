from PIL import Image, ImageEnhance
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
ACT = os.path.join(ROOT, "assets", "models", "actors")
UI = os.path.join(ROOT, "assets", "ui")

# Darius is the reference: his head fills about two thirds of the frame, with the shoulders just
# visible. 0.235 was too tight (head filled everything), 0.46 too loose. Split the difference.
JOBS = (
    ("maya_t_0.png", "maya_hd_portrait.png", "maya_hud_gray.png", 0.32, 0.04),
    ("riley_t_0.png", "riley_hd_portrait.png", "riley_hud_gray.png", 0.32, 0.08),
)

for src, dst, gray, frac, drop in JOBS:
    im = Image.open(os.path.join(ACT, src)).convert("RGBA")
    x0, y0, x1, y1 = im.split()[3].getbbox()
    h = y1 - y0
    side = int(h * frac)
    cx = (x0 + x1) // 2
    top = max(0, y0 + int(side * drop))
    crop = im.crop((cx - side // 2, top, cx + side // 2, top + side)).resize((512, 512), Image.LANCZOS)
    crop.save(os.path.join(UI, dst))
    ImageEnhance.Brightness(crop.convert("LA").convert("RGBA")).enhance(0.72).save(os.path.join(UI, gray))
    print(dst, "side", side, "top", top)
