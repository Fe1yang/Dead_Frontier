import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old1 = "\t# (trash cans removed: the grey cylinder read as junk standing on the road)"
new1 = ('\t# trash cans live out past the kerb line, at 12 m from the centre\n'
        '\tif rng_d.randf() < 0.16:\n'
        '\t\t_prop_node("trash_can", road, Vector3(side * 12.0, PAVEMENT_Y, base_z + rng_d.randf_range(-6.0, 6.0)), 0.0)')
assert t.count(old1) == 1, t.count(old1)
t = t.replace(old1, new1, 1)

old2 = "\t\t# (trash cans removed)"
new2 = ('\t\tif decor_rng.randf() < 0.26:\n'
        '\t\t\t_prop_node("trash_can", road, Vector3(side * 12.0, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.0, 6.0)), side * PI * 0.5)')
assert t.count(old2) == 1, t.count(old2)
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("trash cans spawn at x = +-12")
