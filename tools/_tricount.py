import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models"

files = [
    r"\actors\survivor_medic_universal.glb",
    r"\actors\zombie_walker_universal.glb",
    r"\actors\zombie_banshee_universal.glb",
    r"\actors\zombie_juggernaut_universal.glb",
    r"\weapons\rifle.glb",
    r"\weapons\flame.glb",
    r"\pets\white_tiger.glb",
]

for rel in files:
    p = base + rel
    try:
        d = open(p, "rb").read()
    except OSError:
        print("missing", rel)
        continue
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    tris = 0
    for m in doc.get("meshes", []):
        for pr in m["primitives"]:
            idx = pr.get("indices")
            if idx is not None:
                tris += doc["accessors"][idx]["count"] // 3
            else:
                pos = pr.get("attributes", {}).get("POSITION")
                if pos is not None:
                    tris += doc["accessors"][pos]["count"] // 3
    mb = len(d) / 1048576.0
    print("%-42s %8d tris  %6.1f MB" % (rel.strip("\\"), tris, mb))
