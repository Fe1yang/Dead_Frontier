from PIL import Image, ImageEnhance
import os, shutil

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
act = os.path.join(ROOT, "assets", "models", "actors")
ui = os.path.join(ROOT, "assets", "ui")

SIDE = 250      # fixed crop: identical head size for every character, arms cropped out
TOP_PAD = 8

jobs = (
    ("head_survivor_riley_universal.png", "riley_hd_portrait.png", "riley_hud_gray.png"),
    ("head_survivor_maya_universal.png", "maya_hd_portrait.png", "maya_hud_gray.png"),
)

for src, dst, gray in jobs:
    im = Image.open(os.path.join(act, src)).convert("RGBA")
    x0, y0, x1, y1 = im.split()[3].getbbox()
    cx = (x0 + x1) // 2
    top = max(0, y0 - TOP_PAD)
    box = (cx - SIDE // 2, top, cx + SIDE // 2, top + SIDE)
    crop = im.crop(box).resize((512, 512), Image.LANCZOS)
    crop.save(os.path.join(ui, dst))
    ImageEnhance.Brightness(crop.convert("LA").convert("RGBA")).enhance(0.72).save(os.path.join(ui, gray))
    print(dst, "box", box)

shutil.copyfile(os.path.join(ui, "maya_hd_portrait.png"), os.path.join(ui, "store", "char_maya.png"))
print("done")
