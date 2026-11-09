import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

helper = '''## Street furniture, placed the way a real pavement works: things that belong against a wall sit
## at the curb line, the rest is scattered sparsely. Each district gets its own mix so the blocks
## do not look identical, and the lamp style varies block by block.
const PROP_DIR := "res://assets/models/props/"


func _prop_node(name: String, parent: Node3D, pos: Vector3, yaw: float = 0.0) -> Node3D:
	var path := PROP_DIR + name + ".glb"
	if not ResourceLoader.exists(path):
		return null
	var node := (load(path) as PackedScene).instantiate() as Node3D
	node.position = pos
	node.rotation.y = yaw
	parent.add_child(node)
	return node


func _decorate_district(road: Node3D, index: int) -> void:
	var decor_rng := RandomNumberGenerator.new()
	decor_rng.seed = 0x5EED + index * 977
	# --- lamps: three block types, so lighting differs from street to street -----------------
	var lamp_style := index % 3
	if lamp_style != 2:
		var lamp_name := "lamp_modern" if lamp_style == 0 else "lamp_round"
		for side in [-1.0, 1.0]:
			_prop_node(lamp_name, road, Vector3(side * 3.85, 0.0, 2.4), 0.0)
			_prop_node(lamp_name, road, Vector3(side * 3.85, 0.0, -5.4), 0.0)
	# --- things that stand against the buildings --------------------------------------------
	for side in [-1.0, 1.0]:
		var x_wall: float = side * 4.85
		if decor_rng.randf() < 0.34:
			_prop_node("trash_bin", road, Vector3(x_wall, 0.0, decor_rng.randf_range(-6.0, 6.0)), side * PI * 0.5)
		if decor_rng.randf() < 0.26:
			_prop_node("trash_can", road, Vector3(side * 4.55, 0.0, decor_rng.randf_range(-6.0, 6.0)), side * PI * 0.5)
		if decor_rng.randf() < 0.18:
			_prop_node("phone_booth", road, Vector3(x_wall, 0.0, decor_rng.randf_range(-5.0, 5.0)), side * PI * 0.5)
		if decor_rng.randf() < 0.30:
			_prop_node("bench", road, Vector3(side * 4.45, 0.0, decor_rng.randf_range(-5.5, 5.5)), side * PI * 0.5)
		if decor_rng.randf() < 0.22:
			_prop_node("hydrant", road, Vector3(side * 4.35, 0.0, decor_rng.randf_range(-6.5, 6.5)), 0.0)
		# manholes sit along the pavement line, roughly aligned with the street
		if decor_rng.randf() < 0.30:
			_prop_node("manhole", road, Vector3(side * 4.2 + decor_rng.randf_range(-0.15, 0.15), 0.012, decor_rng.randf_range(-6.0, 6.0)), 0.0)
	# --- litter: a couple of cans, not a carpet ---------------------------------------------
	var cans := decor_rng.randi_range(0, 3)
	for i in range(cans):
		var can_name: String = ["can_a", "can_b", "can_c", "can_d"][decor_rng.randi_range(0, 3)]
		var cx: float = decor_rng.randf_range(3.75, 4.75) * (1.0 if decor_rng.randf() < 0.5 else -1.0)
		_prop_node(can_name, road, Vector3(cx, 0.0, decor_rng.randf_range(-7.0, 7.0)), decor_rng.randf_range(0.0, TAU))


'''
anchor = "func _build_road() -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

# call it right after the district is dressed
old_call = "\tEnvironmentMaterials.apply(road,i); DisasterDressing.apply(road,i,ZombieScript); roads.append(road)"
assert t.count(old_call) == 1
t = t.replace(old_call, old_call + "\n\t_decorate_district(road, i)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("street furniture decorator added")
