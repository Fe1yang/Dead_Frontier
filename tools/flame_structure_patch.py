import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the cone already touches crates and barrels, but it only ever counted as ONE hit point, so a
# pedestal took a full magazine of flame to break. Give the flame real structural damage.
old_crate = '''		crate.take_hit()
		hit += 1'''
new_crate = '''		# a flamethrower should chew through a supply case, not tick it one hit at a time
		crate.take_hit(FLAME_STRUCTURE_DAMAGE)
		hit += 1'''
assert t.count(old_crate) == 1
t = t.replace(old_crate, new_crate, 1)

old_barrel = '''		barrel.take_hit(FLAME_TICK_DAMAGE)'''
if t.count(old_barrel) == 1:
    t = t.replace(old_barrel, '''		barrel.take_hit(FLAME_STRUCTURE_DAMAGE)''', 1)

anchor = "const FLAME_BURN_FRACTION := 0.06"
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + "\n## Damage per flame tick against crates and barrels (they have hit points, not health).\nconst FLAME_STRUCTURE_DAMAGE := 3", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame now does real damage to crates and barrels")
