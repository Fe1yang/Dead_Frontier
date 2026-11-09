import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

# every long gun matches the assault rifle; the pistols share the small scale
for key in ("SMG", "SHOTGUN", "SNIPER", "LAUNCHER"):
    for old_val in ("1.05", "0.95", "0.85"):
        old = '"%s":%s' % (key, old_val)
        if t.count(old) == 1:
            t = t.replace(old, '"%s":1.43' % key, 1)
            break

io.open(p, "w", encoding="utf-8", newline="\n").write(t)

line = [l for l in t.split("\n") if l.startswith("const WEAPON_SCALES")][0]
print(line[:170])
