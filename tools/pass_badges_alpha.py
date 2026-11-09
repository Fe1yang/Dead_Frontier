from PIL import Image

for name in ("pass_weekly.png", "pass_monthly.png"):
    p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\ui\store" + "\\" + name
    im = Image.open(p).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            # the sheet ships on white: drop everything close to it
            if r > 244 and g > 244 and b > 244:
                px[x, y] = (r, g, b, 0)
    im.save(p)
    print(name, "white background removed")
