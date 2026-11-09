import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

repl = (
    # measured: asphalt spans -4.18..4.18, curb sits at 4.36, buildings start near 7.8
    ("\t\t\t_prop_node(lamp_name, road, Vector3(side * 3.85, 0.0, 2.4), 0.0)\n"
     "\t\t\t_prop_node(lamp_name, road, Vector3(side * 3.85, 0.0, -5.4), 0.0)",
     "\t\t\t_prop_node(lamp_name, road, Vector3(side * 4.62, 0.0, 2.4), 0.0)\n"
     "\t\t\t_prop_node(lamp_name, road, Vector3(side * 4.62, 0.0, -5.4), 0.0)"),
    ("\t\tvar x_wall: float = side * 4.85", "\t\tvar x_wall: float = side * 6.55"),
    ('\t\t\t_prop_node("trash_can", road, Vector3(side * 4.55, 0.0,', '\t\t\t_prop_node("trash_can", road, Vector3(side * 5.45, 0.0,'),
    ('\t\t\t_prop_node("bench", road, Vector3(side * 4.45, 0.0,', '\t\t\t_prop_node("bench", road, Vector3(side * 5.25, 0.0,'),
    ('\t\t\t_prop_node("hydrant", road, Vector3(side * 4.35, 0.0,', '\t\t\t_prop_node("hydrant", road, Vector3(side * 4.90, 0.0,'),
    ('\t\t\t_prop_node("manhole", road, Vector3(side * 4.2 + decor_rng.randf_range(-0.15, 0.15), 0.012,',
     '\t\t\t_prop_node("manhole", road, Vector3(side * 5.35 + decor_rng.randf_range(-0.15, 0.15), 0.012,'),
    ("\t\tvar cx: float = decor_rng.randf_range(3.75, 4.75) * (1.0 if decor_rng.randf() < 0.5 else -1.0)",
     "\t\tvar cx: float = decor_rng.randf_range(4.55, 6.6) * (1.0 if decor_rng.randf() < 0.5 else -1.0)"),
)

for old, new in repl:
    assert t.count(old) == 1, old[:60]
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props moved off the asphalt onto the pavement")
