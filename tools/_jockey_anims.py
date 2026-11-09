import json
import struct
import sys

sys.stdout.reconfigure(encoding="ascii", errors="backslashreplace")

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\models\actors"
for n in ("zombie_jockey_universal", "zombie_jockey_hd", "zombie_jockey_new_hd", "zombie_jockey"):
    p = base + "\\" + n + ".glb"
    try:
        d = open(p, "rb").read()
    except OSError:
        continue
    ln, _ = struct.unpack("<II", d[12:20])
    doc = json.loads(d[20:20 + ln].decode("utf-8", "ignore"))
    print(n, "anims:", [a.get("name") for a in doc.get("animations", [])])
