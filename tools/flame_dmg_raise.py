import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old_const = "const FLAME_STRUCTURE_HITS := 3"
new_const = "const FLAME_STRUCTURE_HITS := 60   # flame melts a case: one burst is enough"
assert t.count(old_const) == 1, t.count(old_const)
t = t.replace(old_const, new_const, 1)

old_barrel = "barrel.take_hit(FLAME_STRUCTURE_HITS * 8.0)"
new_barrel = "barrel.take_hit(400.0)"
assert t.count(old_barrel) == 1, t.count(old_barrel)
t = t.replace(old_barrel, new_barrel, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame now melts crates (60 hits) and barrels (400 damage) per tick")
