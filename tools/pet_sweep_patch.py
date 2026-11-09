import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	# queue_free is deferred, so a fast switch could leave the previous animal on stage and
	# the tiger and lion ended up standing inside each other. Sweep every tagged pet first.
	for child in get_children():
		if child.has_meta("lobby_pet"):
			child.visible = false
			if child.get_parent() != null:
				child.get_parent().remove_child(child)
			child.queue_free()
	add_child(pet); pet.set_meta("lobby_pet", true); ModelFix.double_sided(pet)'''

new = '''	# queue_free is deferred, so a fast switch left the previous animal standing inside the new
	# one. Drop EVERY earlier animal reference (meta, name prefix or a pet asset path) before the
	# new one is added, whatever code path created it.
	for child in get_children():
		var is_pet: bool = child.has_meta("lobby_pet") or String(child.name).begins_with("LobbyPet") \\
			or String(child.name).contains("wolfdog") or String(child.name).contains("tiger") \\
			or String(child.name).contains("lion") or String(child.name).contains("mastiff") \\
			or String(child.name).contains("doberman") or String(child.name).contains("shepherd")
		if not is_pet:
			continue
		child.visible = false
		if child.get_parent() != null:
			child.get_parent().remove_child(child)
		child.queue_free()
	pet.name = "LobbyPet"
	add_child(pet); pet.set_meta("lobby_pet", true); ModelFix.double_sided(pet)'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("show_pet sweeps every earlier animal, whatever created it")
