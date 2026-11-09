import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors\pursuer_abomination.glb"
d = open(p, "rb").read()
ln, _ = struct.unpack("<II", d[12:20])
doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))

nodes = doc["nodes"]
parent = {}
for i, n in enumerate(nodes):
    for c in n.get("children", []):
        parent[c] = i

print("meshes:", len([n for n in nodes if "mesh" in n]), " joints:", len(doc["skins"][0]["joints"]))
for i, n in enumerate(nodes):
    if "mesh" not in n:
        continue
    chain = []
    j = i
    depth = 0
    while j in parent and depth < 4:
        j = parent[j]
        chain.append(nodes[j].get("name", "?"))
        depth += 1
    print("%-34s -> %s" % (n.get("name", "?"), " / ".join(chain)))
