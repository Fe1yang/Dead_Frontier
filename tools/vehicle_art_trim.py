from PIL import Image, ImageChops
import glob
import os

BASE = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store"

for p in sorted(glob.glob(os.path.join(BASE, "vehicle_*.png"))):
    im = Image.open(p).convert("RGBA")
    box = im.split()[3].getbbox()
    if box is None or (box[2] - box[0]) < 8:
        diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, (255, 255, 255)))
        box = diff.getbbox() or (0, 0, im.size[0], im.size[1])
    crop = im.crop(box)
    side = int(max(crop.size) * 1.08)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    canvas.resize((512, 512), Image.LANCZOS).save(p)
    print(os.path.basename(p), "was", box, "-> square", side)
