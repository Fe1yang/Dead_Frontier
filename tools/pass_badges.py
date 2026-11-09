from PIL import Image, ImageChops

SRC = r"C:\Users\user\.dsh\attachments\v1\objects\23\23311dd7eecce01bb4a777b823542695438a1ec7154f4e7a0ab1129b7d5eef99"
OUT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store"

im = Image.open(SRC).convert("RGBA")
w, h = im.size
half = w // 2

def trim(img):
    bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
    diff = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, (255, 255, 255)))
    box = diff.getbbox() or (0, 0, img.size[0], img.size[1])
    out = img.crop(box)
    side = int(max(out.size) * 1.06)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(out, ((side - out.size[0]) // 2, (side - out.size[1]) // 2))
    return canvas.resize((512, 512), Image.LANCZOS)

week = im.crop((0, 0, half, h))
month = im.crop((half, 0, w, h))
trim(week).save(OUT + r"\pass_weekly.png")
trim(month).save(OUT + r"\pass_monthly.png")
print("pass_weekly.png and pass_monthly.png written")
