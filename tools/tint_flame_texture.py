from PIL import Image

# The flame quad texture has a white hot core. Keep its alpha, tint the RGB warm orange, so the
# particle ends read orange instead of white dots while the ramped colours stay as designed.
P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\vfx\flame_particle.png"

im = Image.open(P).convert("RGBA")
r, g, b, a = im.split()
# warm orange, roughly (255, 140, 40): white core still reads as fire, never as grey
tint = Image.merge("RGBA", (
    Image.new("L", im.size, 255),
    Image.new("L", im.size, 150),
    Image.new("L", im.size, 45),
    a,
))
tint.save(P)
print("flame_particle.png tinted orange, alpha preserved")
