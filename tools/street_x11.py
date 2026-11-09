import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

helper = '''## The rest of the street furniture, all on the x = 11 line the user settled on. Sparse: most
## blocks get two or three pieces, and litter comes as a small cluster near existing ground junk.
func _place_street_props(road: Node3D, index: int) -> void:
	var rng_d := RandomNumberGenerator.new()
	rng_d.seed = 0xC0FFEE + index * 733
	var side: float = -1.0 if rng_d.randf() < 0.5 else 1.0
	var base_z: float = road.global_position.z
	var x: float = side * 11.0

	if rng_d.randf() < 0.20:
		_prop_node("bench", road, Vector3(x, PAVEMENT_Y, base_z + rng_d.randf_range(-6.0, 6.0)), -side * PI * 0.5)
	if rng_d.randf() < 0.18:
		_prop_node("trash_bin", road, Vector3(x, PAVEMENT_Y, base_z + rng_d.randf_range(-6.0, 6.0)), -side * PI * 0.5)
	if rng_d.randf() < 0.16:
		_prop_node("trash_can", road, Vector3(x, PAVEMENT_Y, base_z + rng_d.randf_range(-6.0, 6.0)), 0.0)
	if rng_d.randf() < 0.22:
		_prop_node("manhole", road, Vector3(x + rng_d.randf_range(-0.12, 0.12), PAVEMENT_Y + 0.01, base_z + rng_d.randf_range(-6.5, 6.5)), 0.0)
	if rng_d.randf() < 0.14:
		_prop_node("hydrant", road, Vector3(x, PAVEMENT_Y, base_z + rng_d.randf_range(-6.5, 6.5)), 0.0)

	# litter: 1-4 cans in one spot, preferably where the block already has ground junk
	if rng_d.randf() < 0.45:
		var near := _junk_spot(road, side)
		var lz: float = near.z if near != Vector3.ZERO else base_z + rng_d.randf_range(-7.0, 7.0)
		var lx: float = near.x if near != Vector3.ZERO else x
		var count: int = rng_d.randi_range(1, 4)
		for i in range(count):
			var can_name: String = ["can_a", "can_b", "can_c", "can_d"][rng_d.randi_range(0, 3)]
			var off := Vector3(rng_d.randf_range(-0.6, 0.6), 0.0, rng_d.randf_range(-0.6, 0.6))
			_prop_node(can_name, road, Vector3(lx, PAVEMENT_Y, lz) + off, rng_d.randf_range(0.0, TAU))


## World position of existing ground junk on one side of the block, or ZERO if there is none.
func _junk_spot(road: Node3D, side: float) -> Vector3:
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var nm := String(mi.name).to_lower()
		if nm.find("garbage") == -1 and nm.find("trash") == -1 and nm.find("weed") == -1 and nm.find("rubble") == -1:
			continue
		var a: AABB = mi.global_transform * mi.get_aabb()
		if side > 0.0 and a.get_center().x < 4.2:
			continue
		if side < 0.0 and a.get_center().x > -4.2:
			continue
		return a.get_center()
	return Vector3.ZERO


'''
anchor = "func _decorate_district(road: Node3D, index: int) -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

old_call = "\t_place_phone_booth(road)"
assert t.count(old_call) == 1
t = t.replace(old_call, old_call + "\n\t_place_street_props(road, i)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("street furniture placed at x = +/-11, litter as a 1-4 cluster near junk")
