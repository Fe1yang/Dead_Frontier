import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\zombie_jockey_universal.glb"
d = open(p, "rb").read()
ln, _ = struct.unpack("<II", d[12:20])
doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
anims = [a.get("name") for a in doc.get("animations", [])]
meshes = len([n for n in doc["nodes"] if "mesh" in n])
skins = len(doc.get("skins", []))
print("anims:", anims)
print("meshes:", meshes, "skins:", skins)
