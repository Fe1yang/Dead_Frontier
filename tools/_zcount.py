import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models"


def info(path):
    d = open(path, "rb").read()
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    meshes = [n for n in doc["nodes"] if "mesh" in n]
    mats = set()
    for n in meshes:
        for pr in doc["meshes"][n["mesh"]]["primitives"]:
            mats.add(pr.get("material", -1))
    return len(meshes), len(mats)


for name in ("zombie_walker", "zombie_runner", "zombie_brute", "zombie_banshee", "zombie_jockey"):
    for folder in ("actors", "zombies", ""):
        p = base + ("\\" + folder if folder else "") + "\\" + name + ".glb"
        try:
            m, mt = info(p)
            print(name, folder or "-", "meshes", m, "materials", mt)
            break
        except OSError:
            continue
