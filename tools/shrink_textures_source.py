"""Downscale the model textures of the truth-source tree to match the packaged clone."""
import os

from PIL import Image

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\models"
LIMIT = 2048
TARGET = 1024

saved = 0
touched = 0
for dirpath, _d, filenames in os.walk(ROOT):
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
        if fn.lower().endswith((".jpg", ".jpeg")):
            im.convert("RGB").save(p, quality=88, optimize=True)
        else:
            im.save(p, optimize=True)
        saved += max(0, before - os.path.getsize(p))
        touched += 1

print("source: downscaled", touched, "saved", round(saved / 1048576.0, 1), "MB")
