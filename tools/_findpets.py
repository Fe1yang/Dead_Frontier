import json
import struct
import sys
import glob
import os

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models"

hits = 0
for path in glob.glob(base + r"\**\*.glb", recursive=True):
    try:
        d = open(path, "rb").read()
    except OSError:
        continue
    ln, _ = struct.unpack("<II", d[12:20])
    try:
        doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    except Exception:
        continue
    names = " ".join(n.get("name", "").lower() for n in doc.get("nodes", []))
    if "lion" in names or "tiger" in names:
        print(os.path.relpath(path, base))
        hits += 1
print("files with lion/tiger nodes:", hits)
