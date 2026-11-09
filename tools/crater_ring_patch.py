import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		for k in range(1):
			var ang := rng_d.randf_range(0.0, TAU)
			_traffic_cone(road, Vector3(CRATER_X + cos(ang) * (CRATER_RADIUS + 0.55), PAVEMENT_Y,
				base_z + sin(ang) * (CRATER_RADIUS + 0.55)))'''

new = '''		# ring of 3..6 cones around the crater mouth, evenly spaced with a little jitter
		var cone_count := rng_d.randi_range(3, 6)
		var ring_r := CRATER_RADIUS + 0.55
		for k in range(cone_count):
			var ang := TAU * float(k) / float(cone_count) + rng_d.randf_range(-0.18, 0.18)
			_traffic_cone(road, Vector3(CRATER_X + cos(ang) * ring_r, PAVEMENT_Y,
				base_z + sin(ang) * ring_r))'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crater ring: 3-6 cones evenly spaced")
