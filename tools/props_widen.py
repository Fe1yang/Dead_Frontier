import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# widen: every prop moves ~25% further out from the centre line
repl = (
    ("var x_wall: float = side * 7.55", "var x_wall: float = side * 9.40"),
    ("side * 7.35", "side * 9.15"),
    ("side * 7.05, PAVEMENT_Y, base_z + 2.4", "side * 8.80, PAVEMENT_Y, base_z + 2.4"),
    ("side * 7.05, PAVEMENT_Y, base_z - 5.4", "side * 8.80, PAVEMENT_Y, base_z - 5.4"),
    ("side * 7.05", "side * 8.80"),
    ("side * 6.95", "side * 8.70"),
    ("side * 7.10 + decor_rng.randf_range(-0.15, 0.15)", "side * 8.85 + decor_rng.randf_range(-0.15, 0.15)"),
    ("decor_rng.randf_range(6.9, 7.75)", "decor_rng.randf_range(8.6, 9.7)"),
)
for old, new in repl:
    if t.count(old) >= 1:
        t = t.replace(old, new)

# and hide the district's own lamp posts that stand in the roadway (measured x around -1.4)
if "hide_road_lamps" not in t:
    helper = '''## Some districts ship their own lamp post standing in the roadway (x around -1.4). Hide those.
func _hide_road_lamps(road: Node3D) -> void:
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		if String(mi.name).to_lower().find("lamp") == -1:
			continue
		if absf(mi.global_position.x) < 4.6:
			mi.visible = false


'''
    anchor = "func _decorate_district(road: Node3D, index: int) -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)
    t = t.replace("\tvar base_z: float = road.global_position.z",
                  "\tvar base_z: float = road.global_position.z\n\t_hide_road_lamps(road)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props widened to ~8.8-9.4 m; district lamps in the roadway hidden")
