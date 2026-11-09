import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '"FLAME": Vector3(0.0, 0.02, 0.52),'
new = '"FLAME": Vector3(-0.48, 0.02, 0.52),'
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame muzzle x compensated by -0.48")
