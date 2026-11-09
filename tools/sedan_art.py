from PIL import Image, ImageChops

BASE = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store"

import os
for name in ("vehicle_sedan.png",):
    p = os.path.join(BASE, name)
    im = Image.open(p).convert("RGBA")
    alpha = im.split()[3]
    box = alpha.getbbox()
    if box is None or (box[2] - box[0]) < 8:
        # no useful alpha: trim against white instead
        diff = ImageChops.difference(im.convert("RGB"), Image.new("RGB", im.size, (255, 255, 255)))
        box = diff.getbbox() or (0, 0, im.size[0], im.size[1])
    crop = im.crop(box)
    side = int(max(crop.size) * 1.08)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    canvas.resize((512, 512), Image.LANCZOS).save(p)
    print(name, "trimmed from", box, "to square", side)
