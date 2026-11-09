import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the flame knocked the hit counter down to zero but never ran the break handler, so the reward
# animation played and nothing was granted
old_crate = '''		crate.take_hit(FLAME_STRUCTURE_HITS)
		hit += 1'''
new_crate = '''		if crate.take_hit(FLAME_STRUCTURE_HITS):
			_break_crate(crate)
		hit += 1'''
assert t.count(old_crate) == 1, t.count(old_crate)
t = t.replace(old_crate, new_crate, 1)

old_barrel = '''		barrel.take_hit(400.0)
		hit += 1'''
new_barrel = '''		if barrel.take_hit(400.0):
			_explode(barrel)
		hit += 1'''
assert t.count(old_barrel) == 1, t.count(old_barrel)
t = t.replace(old_barrel, new_barrel, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame now runs the break/explode handlers, so rewards are granted")
