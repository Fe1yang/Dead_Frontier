import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"

for name in ("zombie_jockey_universal.glb", "zombie_walker_universal.glb"):
    p = base + "\\" + name
    d = open(p, "rb").read()
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    anims = [a.get("name") for a in doc.get("animations", [])]
    joints = len(doc["skins"][0]["joints"]) if doc.get("skins") else 0
    print(name, "joints", joints, "anims", anims)
