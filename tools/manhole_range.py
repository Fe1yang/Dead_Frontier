import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\tif rng_d.randf() < 0.22:\n\t\t_prop_node(\"manhole\", road, Vector3(x + rng_d.randf_range(-0.12, 0.12), PAVEMENT_Y + 0.01, base_z + rng_d.randf_range(-6.5, 6.5)), 0.0)"
new = ("\tif rng_d.randf() < 0.40:\n"
       "\t\t# 10.9 .. 11.3 on whichever pavement this block uses\n"
       "\t\tvar mx: float = x + side * rng_d.randf_range(-0.1, 0.3)\n"
       "\t\t_prop_node(\"manhole\", road, Vector3(mx, PAVEMENT_Y + 0.01, base_z + rng_d.randf_range(-6.5, 6.5)), 0.0)")
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("manholes sit between 10.9 and 11.3, and spawn more often")
