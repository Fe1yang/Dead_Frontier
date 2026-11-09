from PIL import Image, ImageEnhance
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
ACT = os.path.join(ROOT, "assets", "models", "actors")
UI = os.path.join(ROOT, "assets", "ui")

im = Image.open(os.path.join(ACT, "riley_t_0.png")).convert("RGBA")
x0, y0, x1, y1 = im.split()[3].getbbox()
h = y1 - y0
side = int(h * 0.40)
cx = (x0 + x1) // 2
top = max(0, y0 + int(side * 0.03))
crop = im.crop((cx - side // 2, top, cx + side // 2, top + side)).resize((512, 512), Image.LANCZOS)
crop.save(os.path.join(UI, "riley_hd_portrait.png"))
ImageEnhance.Brightness(crop.convert("LA").convert("RGBA")).enhance(0.72).save(os.path.join(UI, "riley_hud_gray.png"))
print("riley cropped at 0.40")
