from PIL import Image
import os

base = r"C:\Users\user\AppData\Local\Temp\vfxbundle\brackeys_vfx_bundle\particles\alpha"
out = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\tools"
names = ["fire_01_a.png", "fire_02_a.png", "flame_01_a.png", "flame_04_a.png"]

tiles = []
for n in names:
    im = Image.open(os.path.join(base, n)).convert("RGBA")
    bg = Image.new("RGBA", im.size, (20, 20, 24, 255))
    bg.alpha_composite(im)
    tiles.append(bg.resize((256, 256)))

sheet = Image.new("RGBA", (512, 512), (0, 0, 0, 255))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % 2) * 256, (i // 2) * 256))
sheet.save(os.path.join(out, "alpha_preview.png"))
print("preview written for", names)
