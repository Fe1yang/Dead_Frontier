import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The grey cylinder that keeps showing up on the ground is the trash can prop. The user does not
# want it at all, so stop spawning it (both decoration passes).
old1 = '''	if rng_d.randf() < 0.16:
		_prop_node("trash_can", road, Vector3(x, PAVEMENT_Y, base_z + rng_d.randf_range(-6.0, 6.0)), 0.0)'''
assert t.count(old1) == 1, t.count(old1)
t = t.replace(old1, '\t# (trash cans removed: the grey cylinder read as junk standing on the road)', 1)

old2 = '''		if decor_rng.randf() < 0.26:
			_prop_node("trash_can", road, Vector3(side * 9.15, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.0, 6.0)), side * PI * 0.5)'''
assert t.count(old2) == 1, t.count(old2)
t = t.replace(old2, '\t\t# (trash cans removed)', 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("trash cans no longer spawn")
