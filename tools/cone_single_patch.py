import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# rarely a single cone, and the crater gets one marker instead of a pair
old = "\t\tif decor_rng.randf() < 0.038:"
new = "\t\tif decor_rng.randf() < 0.015:"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

old_ring = "\t\tfor k in range(2):\n\t\t\tvar ang := TAU * float(k) / 2.0 + rng_d.randf_range(-0.25, 0.25)"
new_ring = "\t\tfor k in range(1):\n\t\t\tvar ang := rng_d.randf_range(0.0, TAU)"
assert t.count(old_ring) == 1, t.count(old_ring)
t = t.replace(old_ring, new_ring, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("cone spawn now 1.5% per block, single marker at the crater")
