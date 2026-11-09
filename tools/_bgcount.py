import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\environment"

tot_mats = 0
bg_mats = 0
for i in range(24):
    p = base + "\\city_hd_%02d.glb" % i
    d = open(p, "rb").read()
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    nodes = doc["nodes"]
    acc = 0
    bg = 0
    for n in nodes:
        if "mesh" not in n:
            continue
        m = doc["meshes"][n["mesh"]]
        used = len({pr.get("material", 0) for pr in m["primitives"]})
        acc += used
        if "background" in n.get("name", "").lower():
            bg += used
    tot_mats += acc
    bg_mats += bg
print("total material slots over 24 districts:", tot_mats)
print("background-only slots:", bg_mats)
