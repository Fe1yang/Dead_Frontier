from PIL import Image
import os
import glob

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\vfx"
for p in sorted(glob.glob(os.path.join(base, "*_soft.png"))):
    im = Image.open(p).convert("RGBA")
    alpha = im.split()[3]
    lo, hi = alpha.getextrema()
    print(os.path.basename(p), im.size, "alpha", lo, "-", hi)
