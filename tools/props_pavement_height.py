import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The pavement sits ~13 cm above the asphalt (kerb height). Props placed at y=0 were sunk to road
# level, which is why they still read as being on the street.
if "PAVEMENT_Y" not in t:
    anchor = "const PROP_DIR := \"res://assets/models/props/\""
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## Kerb height: the pavement surface above the asphalt.\nconst PAVEMENT_Y := 0.14", 1)

# every prop placement gets the pavement height
t = t.replace("Vector3(side * 5.15, 0.0, 2.4)", "Vector3(side * 5.15, PAVEMENT_Y, 2.4)")
t = t.replace("Vector3(side * 5.15, 0.0, -5.4)", "Vector3(side * 5.15, PAVEMENT_Y, -5.4)")
t = t.replace("Vector3(x_wall, 0.0, decor_rng.randf_range(-6.0, 6.0))", "Vector3(x_wall, PAVEMENT_Y, decor_rng.randf_range(-6.0, 6.0))")
t = t.replace("Vector3(x_wall, 0.0, decor_rng.randf_range(-5.0, 5.0))", "Vector3(x_wall, PAVEMENT_Y, decor_rng.randf_range(-5.0, 5.0))")
t = t.replace("Vector3(side * 6.05, 0.0,", "Vector3(side * 6.05, PAVEMENT_Y,")
t = t.replace("Vector3(side * 5.90, 0.0,", "Vector3(side * 5.90, PAVEMENT_Y,")
t = t.replace("Vector3(side * 5.45, 0.0,", "Vector3(side * 5.45, PAVEMENT_Y,")
t = t.replace("Vector3(side * 5.75 + decor_rng.randf_range(-0.15, 0.15), 0.012,", "Vector3(side * 5.75 + decor_rng.randf_range(-0.15, 0.15), PAVEMENT_Y + 0.01,")
t = t.replace("Vector3(cx, 0.0, decor_rng.randf_range(-7.0, 7.0))", "Vector3(cx, PAVEMENT_Y, decor_rng.randf_range(-7.0, 7.0))")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props raised to pavement height")
