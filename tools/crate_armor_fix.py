import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The armour GLB is authored at ~120 m, so the fixed 0.6 table scale made a 70 m vest hover over
# the crate and spin. Normalise oversized models before the table scale is applied.
old = "\t\tweapon_model = packed_model.instantiate() as Node3D\n\t\tweapon_model.scale = Vector3.ONE*float(WEAPON_SCALES.get(weapon_id,0.6))"
new = '''		weapon_model = packed_model.instantiate() as Node3D
		var raw_span := _model_span(weapon_model)
		if raw_span > 2.0:
			# authored in centimetres or metres: bring it to ~1 m before the table scale
			weapon_model.scale = Vector3.ONE * (1.0 / raw_span)
		weapon_model.scale *= Vector3.ONE*float(WEAPON_SCALES.get(weapon_id,0.6))'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

helper = '''## Largest axis of a freshly instantiated model, before any scaling.
func _model_span(node: Node3D) -> float:
	var box := AABB()
	var first := true
	for m in node.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		var a: AABB = mi.get_aabb()
		box = a if first else box.merge(a)
		first = false
	if first:
		return 0.0
	return maxf(box.size.x, maxf(box.size.y, box.size.z))


'''
anchor = "func _center_model(m: Node3D) -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate models normalised (armour no longer 70 m)")
