import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\tools\citykit_export.py"
t = io.open(p, encoding="utf-8").read()

old = "img = bpy.data.images.load(TEX) if TEX and os.path.exists(TEX) else None"
new = (
    "img = bpy.data.images.load(TEX) if TEX and os.path.exists(TEX) else None\n"
    "if img is not None:\n"
    "    # the kit atlas is 8k; a single street prop needs 1024 at most\n"
    "    if img.size[0] > 1024 or img.size[1] > 1024:\n"
    "        img.scale(1024, 1024)\n"
)
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("atlas downscaled on export")
