import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		var near := _junk_spot(road, side)
		var lz: float = near.z if near != Vector3.ZERO else base_z + rng_d.randf_range(-7.0, 7.0)
		var lx: float = near.x if near != Vector3.ZERO else x'''
new = '''		# only the z comes from the junk pile: the cans themselves must stay on 9..12
		var near := _junk_spot(road, side)
		var lz: float = near.z if near != Vector3.ZERO else base_z + rng_d.randf_range(-7.0, 7.0)
		var lx: float = side * rng_d.randf_range(9.0, 12.0)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("litter confined to x 9..12")
