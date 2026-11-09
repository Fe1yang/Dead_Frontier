"""List model files that no script, scene or resource references.

Anything reported here is dead weight in the package: the game never loads it.
"""
import os
import re

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

haystack = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if any(skip in dirpath for skip in (".git", ".godot", "tools", "renders", "docs")):
        continue
    for fn in filenames:
        if fn.endswith((".gd", ".tscn", ".tres", ".cfg", ".godot", ".json", ".md")):
            try:
                haystack.append(open(os.path.join(dirpath, fn), encoding="utf-8", errors="ignore").read())
            except OSError:
                pass
blob = "\n".join(haystack)

unused = []
total = 0
for dirpath, _d, filenames in os.walk(os.path.join(ROOT, "assets", "models")):
    for fn in filenames:
        if not fn.endswith(".glb"):
            continue
        p = os.path.join(dirpath, fn)
        stem = fn[:-4]
        if stem in blob or fn in blob:
            continue
        size = os.path.getsize(p)
        unused.append((size, os.path.relpath(p, ROOT)))
        total += size

unused.sort(reverse=True)
for size, rel in unused:
    print("%6.1f MB  %s" % (size / 1048576.0, rel))
print("----")
print("unused files:", len(unused), "total:", round(total / 1048576.0, 1), "MB")
