import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons"
for name in ("makarov.glb", "pistol_makarov.glb"):
    p = base + "\\" + name
    try:
        d = open(p, "rb").read()
    except OSError:
        print(name, "missing")
        continue
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    names = [n.get("name", "?") for n in doc["nodes"] if "mesh" in n]
    print(name, len(d) // 1024, "KB", "meshes:", names)
