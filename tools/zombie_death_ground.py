import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

helper = '''## Lowest point of the rendered body, in world space. Used to keep a falling body on the road.
func _body_low_y() -> float:
	var low := 1.0e9
	for mi in find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m == null or m.mesh == null:
			continue
		var box: AABB = m.global_transform * m.get_aabb()
		low = minf(low, box.position.y)
	return low


'''
anchor = "func die() -> void:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

# while the death clip plays, lift the model so the body never sinks through the tarmac
old_tick = "\tif dead: return\n\tage += delta"
new_tick = '''	if dead:
		# the death clip pushes the pelvis below the model origin: keep the body on the surface
		if death_played and is_instance_valid(model):
			var low := _body_low_y()
			if low < 0.0:
				model.position.y -= low
		return
	age += delta'''
assert t.count(old_tick) == 1, t.count(old_tick)
t = t.replace(old_tick, new_tick, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("dying bodies are lifted so they never sink into the road")
