import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _psx(path: String, pos: Vector3, yaw: float = 0.0) -> Node3D:'''
new = '''## `tint` multiplies the tile's own material colour; the floor uses it to go dark.
func _psx(path: String, pos: Vector3, yaw: float = 0.0, tint: Color = Color.WHITE) -> Node3D:'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

old_tail = '''	var node := (load(full) as PackedScene).instantiate() as Node3D
	node.position = pos
	node.rotation.y = yaw
	add_child(node)
	return node'''
new_tail = '''	var node := (load(full) as PackedScene).instantiate() as Node3D
	node.position = pos
	node.rotation.y = yaw
	add_child(node)
	if tint != Color.WHITE:
		for mi in node.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			if m.mesh == null or m.mesh.get_surface_count() == 0:
				continue
			var src := m.mesh.surface_get_material(0)
			if src is StandardMaterial3D:
				var copy := (src as StandardMaterial3D).duplicate() as StandardMaterial3D
				copy.albedo_color = tint
				m.material_override = copy
	return node'''
assert t.count(old_tail) == 1
t = t.replace(old_tail, new_tail, 1)

old_floor = '''			_psx("floorWood", Vector3(gx * 4.0 + 2.0, -0.05, gz * 4.0 + 2.0))'''
new_floor = '''			_psx("floorWood", Vector3(gx * 4.0 + 2.0, -0.05, gz * 4.0 + 2.0), 0.0, Color(0.34, 0.30, 0.27))'''
assert t.count(old_floor) == 1
t = t.replace(old_floor, new_floor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("floor darkened")
