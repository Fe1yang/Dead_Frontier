import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The flamethrower had no muzzle entry, so it borrowed the pistol's point: that put the flash and
# the flame origin off to one side of the barrel.
anchor = 'const MUZZLE_POINTS := {'
assert t.count(anchor) == 1
if '"FLAME": Vector3' not in t:
    t = t.replace(anchor, anchor + '\n\t"FLAME": Vector3(0.0, 0.02, 0.52),', 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("explicit flamethrower muzzle point added")
