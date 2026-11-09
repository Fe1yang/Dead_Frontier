import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The district node is scaled, so local coordinates were not metres: a phone booth asked for at
# x=7.1 landed at x~2.5, in the middle of the road. Place props in WORLD space instead.
old = '''func _prop_node(name: String, parent: Node3D, pos: Vector3, yaw: float = 0.0) -> Node3D:
	var path := PROP_DIR + name + ".glb"
	if not ResourceLoader.exists(path):
		return null
	var node := (load(path) as PackedScene).instantiate() as Node3D
	node.position = pos
	node.rotation.y = yaw
	parent.add_child(node)
	return node'''
new = '''func _prop_node(name: String, parent: Node3D, world_pos: Vector3, yaw: float = 0.0) -> Node3D:
	var path := PROP_DIR + name + ".glb"
	if not ResourceLoader.exists(path):
		return null
	var node := (load(path) as PackedScene).instantiate() as Node3D
	parent.add_child(node)
	# world coordinates, because the district node carries a scale and props must not inherit it
	node.global_position = world_pos
	node.global_rotation = Vector3(0.0, yaw, 0.0)
	return node'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

# every call now needs the district's world z added
old_head = '''func _decorate_district(road: Node3D, index: int) -> void:
	var decor_rng := RandomNumberGenerator.new()
	decor_rng.seed = 0x5EED + index * 977'''
new_head = '''func _decorate_district(road: Node3D, index: int) -> void:
	var decor_rng := RandomNumberGenerator.new()
	decor_rng.seed = 0x5EED + index * 977
	var base_z: float = road.global_position.z'''
assert t.count(old_head) == 1
t = t.replace(old_head, new_head, 1)

# rewrite the bodies so the z passed in is a local offset from the district start
t = t.replace('Vector3(x_wall, PAVEMENT_Y, decor_rng.randf_range(-6.0, 6.0))',
              'Vector3(x_wall, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.0, 6.0))')
t = t.replace('Vector3(x_wall, PAVEMENT_Y, decor_rng.randf_range(-5.0, 5.0))',
              'Vector3(x_wall, PAVEMENT_Y, base_z + decor_rng.randf_range(-5.0, 5.0))')
t = t.replace('Vector3(side * 6.60, PAVEMENT_Y, decor_rng.randf_range(-6.0, 6.0))',
              'Vector3(side * 6.60, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.0, 6.0))')
t = t.replace('Vector3(side * 6.35, PAVEMENT_Y, decor_rng.randf_range(-5.5, 5.5))',
              'Vector3(side * 6.35, PAVEMENT_Y, base_z + decor_rng.randf_range(-5.5, 5.5))')
t = t.replace('Vector3(side * 6.15, PAVEMENT_Y, decor_rng.randf_range(-6.5, 6.5))',
              'Vector3(side * 6.15, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.5, 6.5))')
t = t.replace('Vector3(side * 6.20 + decor_rng.randf_range(-0.15, 0.15), PAVEMENT_Y + 0.01, decor_rng.randf_range(-6.0, 6.0))',
              'Vector3(side * 6.20 + decor_rng.randf_range(-0.15, 0.15), PAVEMENT_Y + 0.01, base_z + decor_rng.randf_range(-6.0, 6.0))')
t = t.replace('Vector3(cx, PAVEMENT_Y, decor_rng.randf_range(-7.0, 7.0))',
              'Vector3(cx, PAVEMENT_Y, base_z + decor_rng.randf_range(-7.0, 7.0))')

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props now placed in world space")
