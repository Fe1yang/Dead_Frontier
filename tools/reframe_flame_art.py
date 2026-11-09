from PIL import Image

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store\weapon_flame.png"

im = Image.open(P).convert("RGBA")
x0, y0, x1, y1 = im.split()[3].getbbox()
weapon = im.crop((x0, y0, x1, y1))

# centre the weapon in a square with a small breathing margin, so it fills the card
side = int(max(weapon.size) * 1.10)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(weapon, ((side - weapon.size[0]) // 2, (side - weapon.size[1]) // 2))
canvas.resize((512, 512), Image.LANCZOS).save(P)
print("weapon art reframed:", weapon.size, "->", side)
