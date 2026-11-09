from PIL import Image, ImageEnhance
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
TOOLS = os.path.join(ROOT, "tools")
UI = os.path.join(ROOT, "assets", "ui")

for shot, portrait, gray in (
    ("maya_shot.png", "maya_hd_portrait.png", "maya_hud_gray.png"),
    ("riley_shot.png", "riley_hd_portrait.png", "riley_hud_gray.png"),
):
    im = Image.open(os.path.join(TOOLS, shot)).convert("RGB")
    im = im.resize((512, 512), Image.LANCZOS)
    im.save(os.path.join(UI, portrait))
    g = im.convert("LA").convert("RGB")
    g = ImageEnhance.Brightness(g).enhance(0.72)
    g.save(os.path.join(UI, gray))
    print("installed", portrait, "+", gray)
