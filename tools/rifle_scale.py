import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '"RIFLE":0.95'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, '"RIFLE":1.43', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("rifle preview 0.95 -> 1.43 (1.5x)")
