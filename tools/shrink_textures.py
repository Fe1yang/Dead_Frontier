"""Downscale the model textures that are far larger than the screen can show.

Only files under assets/models are touched: UI art and portraits are left alone. Anything above
2048 px on the long edge becomes 1024, which is still more than a phone screen can resolve at the
distances these props are seen.
"""
import os
import sys

from PIL import Image

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models"
LIMIT = 2048
TARGET = 1024

saved = 0
touched = 0
for dirpath, _dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        p = os.path.join(dirpath, fn)
        before = os.path.getsize(p)
        try:
            im = Image.open(p)
        except Exception:
            continue
        w, h = im.size
        if max(w, h) <= LIMIT:
            continue
        k = TARGET / float(max(w, h))
        im = im.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
        out = p
        if fn.lower().endswith((".jpg", ".jpeg")):
            im.convert("RGB").save(out, quality=88, optimize=True)
        else:
            im.save(out, optimize=True)
        after = os.path.getsize(p)
        saved += max(0, before - after)
        touched += 1

print("downscaled", touched, "textures, saved", round(saved / 1048576.0, 1), "MB")
