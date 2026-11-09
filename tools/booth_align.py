import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

helper = '''## One phone booth per block, standing beside the block's own street shelter and aligned with it.
## If a district has no shelter there is no booth: nothing is dropped at random.
const SHELTER_HINTS := ["shelter", "bus", "awning", "kiosk", "stand", "canopy"]


func _shelter_of(road: Node3D) -> AABB:
	var found := AABB()
	var has := false
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var nm := String(mi.name).to_lower()
		var hit := false
		for hint in SHELTER_HINTS:
			if nm.find(hint) != -1:
				hit = true
				break
		if not hit:
			continue
		var a: AABB = mi.global_transform * mi.get_aabb()
		if absf(a.position.x) < 4.6:
			continue
		found = a if not has else found.merge(a)
		has = true
	return found


func _place_phone_booth(road: Node3D) -> void:
	var shel := _shelter_of(road)
	if shel.size == Vector3.ZERO:
		return
	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# same x line as the shelter, 2.6 m along the street, so neither can overlap the other
	var z := shel.get_center().z + 2.6 * (-1.0 if side < 0.0 else 1.0)
	var x := shel.get_center().x
	_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)


'''
anchor = "func _decorate_district(road: Node3D, index: int) -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

old_call = "\tEnvironmentMaterials.apply(road,i); DisasterDressing.apply(road,i,ZombieScript); roads.append(road)"
assert t.count(old_call) == 1
t = t.replace(old_call, old_call + "\n\t_place_phone_booth(road)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("phone booth placed beside the block's shelter, aligned and separated")
