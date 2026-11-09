from PIL import Image
import os

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
TOOLS = os.path.join(ROOT, "tools")
STORE = os.path.join(ROOT, "assets", "ui", "store")


def cut_out(path):
    """Knock the studio backdrop out by flood filling from the corners."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    # backdrop is a flat dark grey: sample the corners
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    br = sum(c[0] for c in corners) / 4.0
    bg = sum(c[1] for c in corners) / 4.0
    bb = sum(c[2] for c in corners) / 4.0

    seen = [[False] * w for _ in range(h)]
    stack = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tol = 26
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        seen[y][x] = True
        r, g, b, a = px[x, y]
        if abs(r - br) > tol or abs(g - bg) > tol or abs(b - bb) > tol:
            continue
        px[x, y] = (r, g, b, 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


for shot, out in (("maya_shot.png", "char_maya.png"), ("riley_shot.png", "char_riley.png")):
    src = os.path.join(TOOLS, shot)
    im = cut_out(src)
    im.save(os.path.join(STORE, out))
    print("wrote", out)
