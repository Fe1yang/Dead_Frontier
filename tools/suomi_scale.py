import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# pedestal / barrel preview: Suomi matches the assault rifle
p = ROOT + r"\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()
if '"SUOMI"' not in t:
    old = '"RIFLE":1.43'
    assert t.count(old) == 1
    t = t.replace(old, '"RIFLE":1.43,"SUOMI":1.43', 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("crate preview: SUOMI = 1.43 (same as rifle)")
else:
    print("crate preview already has SUOMI")

# armory stage: make sure the Suomi is not scaled down there either
p2 = ROOT + r"\scripts\main_3d.gd"
m = io.open(p2, encoding="utf-8").read()
if '"SUOMI": 1.0' in m and '"SUOMI": 1.0' not in m:
    pass
print("armory size map:", '"SUOMI": 1.0' in m)
