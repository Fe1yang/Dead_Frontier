import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func muzzle_position() -> Vector3:
	if is_instance_valid(weapon_model):
		var pt: Vector3=MUZZLE_POINTS.get(weapon,MUZZLE_POINTS["PISTOL"])'''
new = '''func muzzle_position() -> Vector3:
	# The steampunk flamethrower's origin sits off-centre, so a fixed local point landed beside the
	# barrel. Take the point on its own bounding box that faces furthest along the aim instead.
	if weapon == "FLAME" and is_instance_valid(weapon_model):
		var box := AABB()
		var first := true
		for m in weapon_model.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a)
			first = false
		if not first:
			var dir := aim_direction.normalized()
			if dir.length() < 0.01:
				dir = Vector3.FORWARD
			var half := box.size * 0.5
			var reach: float = absf(dir.x) * half.x + absf(dir.y) * half.y + absf(dir.z) * half.z
			return box.get_center() + dir * reach
	if is_instance_valid(weapon_model):
		var pt: Vector3=MUZZLE_POINTS.get(weapon,MUZZLE_POINTS["PISTOL"])'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame muzzle now derived from the model's own box along the aim")
