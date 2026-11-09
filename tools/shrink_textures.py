"""Shrink every imported texture without touching the source artwork.

The iOS package was 2.18 GB because each texture is imported losslessly at full resolution
(the .godot cache alone is 3.5 GB). Setting a size limit and VRAM compression in the .import
files makes Godot downscale on import, which is what actually ships.
"""
import io
import os
import re

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets"
SIZE_LIMIT = 1024

changed = 0
for dirpath, _dirnames, filenames in os.walk(ROOT):
    for name in filenames:
        if not name.endswith(".import"):
            continue
        path = os.path.join(dirpath, name)
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        if "importer=\"texture\"" not in text:
            continue
        orig = text

        # VRAM compression (S3TC/ETC2/ASTC depending on platform) instead of lossless RGBA
        text = re.sub(r"compress/mode=\d+", "compress/mode=2", text)
        text = re.sub(r"compress/high_quality=\w+", "compress/high_quality=false", text)

        # downscale on import
        if "process/size_limit" in text:
            text = re.sub(r"process/size_limit=\d+", "process/size_limit=%d" % SIZE_LIMIT, text)
        else:
            text = text.replace("[params]\n", "[params]\n\nprocess/size_limit=%d\n" % SIZE_LIMIT, 1)

        if text != orig:
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            changed += 1

print("texture import files updated:", changed)
