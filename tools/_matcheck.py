import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\environment"


def info(path):
    d = open(path, "rb").read()
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    mats = doc.get("materials", [])
    with_tex = 0
    for m in mats:
        if m.get("pbrMetallicRoughness", {}).get("baseColorTexture"):
            with_tex += 1
    names = [m.get("name", "?") for m in mats]
    meshes = [n.get("name", "?") for n in doc["nodes"] if "mesh" in n]
    return len(mats), with_tex, names[:6], len(meshes)


for label, p2 in (
    ("original", base + r"\city_hd_00.glb"),
    ("atlas", base + r"\atlas\city_hd_00.glb"),
):
    n, t, names, nmesh = info(p2)
    print(label, "materials", n, "with texture", t, "meshes", nmesh)
    print("   ", names)
