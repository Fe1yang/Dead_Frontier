import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '"PISTOL":1.25'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, '"PISTOL":0.62', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pistol preview 1.25 -> 0.62 (half size)")
