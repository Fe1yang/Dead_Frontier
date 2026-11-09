from PIL import Image, ImageChops

SRC = r"C:\Users\user\.dsh\attachments\v1\objects\62\620dc04feeb8ff55edc22d6cc06493aff3133412f30b03495b00ea9d803c445d"
OUT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store"

im = Image.open(SRC).convert("RGBA")
w, h = im.size
half = w // 2


def prep(img, name):
    diff = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, (255, 255, 255)))
    box = diff.getbbox() or (0, 0, img.size[0], img.size[1])
    crop = img.crop(box)
    side = int(max(crop.size) * 1.06)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2))
    canvas = canvas.resize((512, 512), Image.LANCZOS)
    px = canvas.load()
    for y in range(512):
        for x in range(512):
            r, g, b, a = px[x, y]
            if r > 246 and g > 246 and b > 246:
                px[x, y] = (r, g, b, 0)
    canvas.save(OUT + "\\" + name)
    print(name, "from", box)


prep(im.crop((0, 0, half, h)), "pass_weekly.png")
prep(im.crop((half, 0, w, h)), "pass_monthly.png")
