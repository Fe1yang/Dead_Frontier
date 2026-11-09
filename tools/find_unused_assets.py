import os
import re

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# every text file that could name an asset
text_exts = (".gd", ".tscn", ".tres", ".godot", ".cfg", ".json")
haystack = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", ".godot", "tools", "diagnostics", ".venv-model", "references", "research")]
    for fn in filenames:
        if fn.endswith(text_exts):
            try:
                haystack.append(open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore").read())
            except OSError:
                pass
blob = "\n".join(haystack).lower()

rows = []
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "assets", "models")):
    dirnames[:] = [d for d in dirnames if d not in (".godot",)]
    for fn in filenames:
        if not fn.lower().endswith((".glb", ".gltf", ".fbx", ".png", ".jpg", ".exr", ".hdr")):
            continue
        full = os.path.join(dirpath, fn)
        size = os.path.getsize(full)
        if size < 2 * 1024 * 1024:
            continue
        base = fn.lower()
        rows.append((size, os.path.relpath(full, ROOT), base in blob))

rows.sort(reverse=True)
total_unused = 0
for size, rel, used in rows[:25]:
    print("%7.1f MB  %-8s %s" % (size / 1048576.0, "USED" if used else "unused", rel))
    if not used:
        total_unused += size
print("----")
print("unused among the listed: %.1f MB" % (total_unused / 1048576.0))
