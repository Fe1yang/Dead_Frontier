import io
import re

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# 1) tag the props where they are made
old_tag = '''	node.global_position = pos
	node.global_rotation = Vector3(0.0, yaw, 0.0)
	return node'''
new_tag = '''	node.global_position = pos
	node.global_rotation = Vector3(0.0, yaw, 0.0)
	# Tagged at creation: these nodes get auto-generated names, so the reveal queue could never
	# recognise them by name.
	node.set_meta("street_prop", true)
	return node'''
assert t.count(old_tag) == 1, t.count(old_tag)
t = t.replace(old_tag, new_tag, 1)

# 2) replace the whole selection block by identity + name fallback
start = t.find("func _stage_district_reveal(road: Node3D) -> void:")
assert start > 0
end = t.find("\tif items.is_empty():", start)
assert end > start

replacement = '''func _stage_district_reveal(road: Node3D) -> void:
	var items: Array = []
	for child in road.get_children():
		if not (child is Node3D):
			continue
		var tagged: bool = child.has_meta("street_prop")
		var nm := String(child.name)
		var by_name := nm.begins_with("phone_booth") or nm.begins_with("bench") or nm.begins_with("trash_") \\
			or nm.begins_with("manhole") or nm.begins_with("hydrant") or nm.begins_with("can_") \\
			or nm.begins_with("lamp")
		if (tagged or by_name) and (child as Node3D).visible:
			(child as Node3D).visible = false
			items.append(child)
'''
t = t[:start] + replacement + t[end:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("reveal selection now uses the tag first")
