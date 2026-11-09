import json
import os
import struct

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

missing = []
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "assets", "models")):
    for fn in filenames:
        if not fn.lower().endswith(".glb"):
            continue
        full = os.path.join(dirpath, fn)
        try:
            with open(full, "rb") as f:
                data = f.read()
            # first chunk is JSON
            length = struct.unpack_from("<I", data, 12)[0]
            js = data[20:20 + length].decode("utf-8", "ignore")
            doc = json.loads(js)
        except Exception:
            continue
        for img in doc.get("images", []):
            uri = img.get("uri")
            if not uri:
                continue
            target = os.path.normpath(os.path.join(dirpath, uri))
            if not os.path.exists(target):
                missing.append((os.path.relpath(full, ROOT), uri))

print("models with a missing external texture:", len(missing))
for m, uri in missing[:20]:
    print("  ", m, "->", uri)
