import json
import struct

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\environment\city_hd_00.glb"
d = open(p, "rb").read()
ln, _ = struct.unpack("<II", d[12:20])
doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
hits = [n.get("name", "") for n in doc["nodes"]
        if "cone" in n.get("name", "").lower() or "traffic" in n.get("name", "").lower()]
print("CONE_NODES", hits)
print("TOTAL_NODES", len(doc["nodes"]))
print("SAMPLE", [n.get("name", "") for n in doc["nodes"]][:12])
