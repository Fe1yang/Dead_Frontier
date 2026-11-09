from PIL import Image
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui"
for n in ("medic_hd_portrait.png", "male_hd_portrait.png", "maya_hd_portrait.png", "riley_hd_portrait.png"):
    p = os.path.join(ROOT, n)
    if not os.path.exists(p):
        print(n, "missing")
        continue
    im = Image.open(p)
    print(n, im.size)
