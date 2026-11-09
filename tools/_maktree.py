import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\weapons\makarov.glb"
d = open(p, "rb").read()
ln, _ = struct.unpack("<II", d[12:20])
doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
print("nodes:", [n.get("name") for n in doc["nodes"]])
print("meshes:", [(m.get("name"), len(m["primitives"])) for m in doc.get("meshes", [])])
