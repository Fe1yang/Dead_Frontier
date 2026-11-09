import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

# a deterministic registry: every animal this scene ever added is tracked and freed on switch
if "var _pet_nodes" not in t:
    anchor = "var pet_shadow: MeshInstance3D"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## Every animal this scene ever put on stage, so a switch can free all of them.\nvar _pet_nodes: Array = []", 1)

start = t.find("\t# queue_free is deferred, so a fast switch left the previous animal standing inside the new")
end = t.find("add_child(pet); pet.set_meta(\"lobby_pet\", true); ModelFix.double_sided(pet)", start)
assert start > 0 and end > start

replacement = '''	# queue_free is deferred, so a fast switch could leave the previous animal standing inside the
	# new one. Every animal is registered, and every registered animal is dropped here.
	for old in _pet_nodes:
		if is_instance_valid(old):
			old.visible = false
			if old.get_parent() != null:
				old.get_parent().remove_child(old)
			old.queue_free()
	_pet_nodes.clear()
	pet.name = "LobbyPet"
'''
t = t[:start] + replacement + t[end:]
t = t.replace(
    'add_child(pet); pet.set_meta("lobby_pet", true); ModelFix.double_sided(pet)',
    'add_child(pet); pet.set_meta("lobby_pet", true); ModelFix.double_sided(pet)\n\t_pet_nodes.append(pet)',
    1,
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pet registry in place")
