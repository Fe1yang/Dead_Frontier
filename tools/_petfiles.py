import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models"


def nodes(rel):
    p = base + "\\" + rel
    d = open(p, "rb").read()
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    names = [n.get("name", "") for n in doc.get("nodes", [])]
    return len(d), names


for rel in (r"pets\lion.glb", r"actors\lion.glb", r"pets\white_tiger.glb", r"actors\white_tiger.glb",
            r"pets\zombie_jockey_universal.glb", r"pets\bus_stop.glb"):
    try:
        size, names = nodes(rel)
    except OSError:
        print("%-42s MISSING" % rel)
        continue
    animals = [n for n in names if any(k in n.lower() for k in ("lion", "tiger", "dog", "cat", "zombie", "stop"))]
    print("%-42s %8d bytes  nodes=%d  '%s'" % (rel, size, len(names), ",".join(animals[:6])))
