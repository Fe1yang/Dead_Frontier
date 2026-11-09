from PIL import Image
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
SRC = r"C:\Users\user\.dsh\attachments\v1\objects\a1\a108e752e16a0331f67f0d99fce638152d5be1ff62e18354580a7a5c4592b759"

img = Image.open(SRC).convert("RGB")
w, h = img.size

# portrait cover for a phone: crop the art to 9:16 without squashing it
target_w = int(h * 9 / 16)
if target_w <= w:
    left = (w - target_w) // 2
    img = img.crop((left, 0, left + target_w, h))
else:
    target_h = int(w * 16 / 9)
    top = (h - target_h) // 2
    img = img.crop((0, top, w, top + target_h))

img = img.resize((1080, 1920), Image.LANCZOS)
out = os.path.join(ROOT, "assets", "ui", "cover.png")
img.save(out)
print("cover written", img.size, os.path.getsize(out))
