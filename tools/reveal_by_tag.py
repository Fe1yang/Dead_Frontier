import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- 1) tag every street prop at creation
old = '''	node.global_position = pos
	node.global_rotation = Vector3(0.0, yaw, 0.0)
	return node'''
new = '''	node.global_position = pos
	node.global_rotation = Vector3(0.0, yaw, 0.0)
	# Tagged here so the reveal queue can find props by identity instead of guessing at names:
	# these nodes are created in code and carry auto-generated names.
	node.set_meta("street_prop", true)
	return node'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# ---------------------------------------------------------------- 2) reveal uses the tag, name prefixes as fallback
old_stage = '''	var items: Array = []
	for child in road.get_children():
		var nm := String(child.name)
		if nm.begins_with("phone_booth") or nm.begins_with("bench") or nm.begins_with("trash_") \\
			or nm.begins_with("manhole") or nm.begins_with("hydrant") or nm.begins_with("can_") \\
			or nm.begins_with("lamp"):
			if child is Node3D and (child as Node3D).visible:
				(child as Node3D).visible = false
				items.append(child)'''
new_stage = '''	var items: Array = []
	for child in road.get_children():
		if not (child is Node3D):
			continue
		var tagged: bool = child.has_meta("street_prop")
		var nm := String(child.name)
		var by_name := nm.begins_with("phone_booth") or nm.begins_with("bench") or nm.begins_with("trash_") \\
			or nm.begins_with("manhole") or nm.begins_with("hydrant") or nm.begins_with("can_") \\
			or nm.begins_with("lamp")
		if tagged or by_name:
			if (child as Node3D).visible:
				(child as Node3D).visible = false
				items.append(child)'''
assert t.count(old_stage) == 1, t.count(old_stage)
t = t.replace(old_stage, new_stage, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("street props are tagged and now join the staged reveal")
