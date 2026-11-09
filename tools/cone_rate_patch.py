import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# pavement cones were on a 30% roll per block: drop to one eighth of that
old = "\t\tif decor_rng.randf() < 0.30:\n\t\t\t_traffic_cone(road, Vector3(side * 8.45"
new = "\t\tif decor_rng.randf() < 0.038:\n\t\t\t_traffic_cone(road, Vector3(side * 8.45"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# the crater ring: keep it, but it only matters on the one district that owns the crater
old_ring = "\t\tfor k in range(3):\n\t\t\tvar ang := TAU * float(k) / 3.0 + rng_d.randf_range(-0.25, 0.25)"
new_ring = "\t\tfor k in range(2):\n\t\t\tvar ang := TAU * float(k) / 2.0 + rng_d.randf_range(-0.25, 0.25)"
assert t.count(old_ring) == 1
t = t.replace(old_ring, new_ring, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("cone chance 0.30 -> 0.038 (about 1/8), crater ring 3 -> 2")
