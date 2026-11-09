import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pickup_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	model_instance.scale = Vector3.ONE * float(DISPLAY_SCALES[kind])
	model_instance.position.y = float(GROUND_OFFSETS[kind])'''
new = '''	model_instance.scale = Vector3.ONE * float(DISPLAY_SCALES[kind])
	# The armour GLB is authored at ~120 m, so a fixed display scale made a 60 m vest spin over the
	# road. Normalise every pickup to its own footprint instead: at most half a metre across.
	var span := _model_span(model_instance)
	if span > 1.0:
		model_instance.scale *= 0.55 / span
	model_instance.position.y = float(GROUND_OFFSETS[kind])'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

helper = '''## Largest axis of the instantiated model, in its own space.
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
anchor = "func _ready() -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pickups normalised by their own bounds")
