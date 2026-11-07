"""Re-cut store pack art with edge flood-fill alpha (not global colour key)."""
from PIL import Image
import glob
import os

SRC = r"C:\Users\user\Documents\kimi\tasks\2026-11-02\20-32-30-26dbcd78\assets\ui\store"

def cutout(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    def is_bg(x, y):
        r, g, b, a = px[x, y]
        return a == 0 or (0.299 * r + 0.587 * g + 0.114 * b) / 255.0 < 0.16

    while stack:
        x, y = stack.pop()
        if x < 0 or x >= w or y < 0 or y >= h or seen[y][x]:
            continue
        seen[y][x] = True
        if not is_bg(x, y):
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                stack.append((nx, ny))
    for y in range(h):
        for x in range(w):
            if seen[y][x] and is_bg(x, y):
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 0)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    out = path.replace(".png", "_recut.png")
    if not os.path.exists(path + ".bak.png"):
        Image.open(path).save(path + ".bak.png")
    im.save(out)
    print(out, im.size)

for p in sorted(glob.glob(os.path.join(SRC, "*.png"))):
    if "_recut" in p:
        continue
    cutout(p)
