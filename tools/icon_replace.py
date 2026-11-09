from PIL import Image
import os
import glob

SRC = r"C:\Users\user\.dsh\attachments\v1\objects\a1\a108e752e16a0331f67f0d99fce638152d5be1ff62e18354580a7a5c4592b759"
ICON_DIR = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\icons"

src = Image.open(SRC).convert("RGBA")
print("source", src.size)

# keep every icon at its existing pixel size, just replace the artwork
for path in sorted(glob.glob(os.path.join(ICON_DIR, "icon-*.png"))):
    if path.endswith(".import"):
        continue
    old = Image.open(path)
    size = old.size
    out = src.resize(size, Image.LANCZOS)
    out.save(path)
    print("replaced", os.path.basename(path), size)
