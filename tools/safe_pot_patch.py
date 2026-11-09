import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	var glass_node:=safe.find_child("Safe_glass",true,false) as MeshInstance3D'''
new = '''	# A green sphere-like prop (the ceramic pots) pokes through the door slab; drop the pots.
	for pot_name in ["Safe_ceramic", "Safe_ceramic_blue"]:
		var pot := safe.find_child(pot_name, true, false) as MeshInstance3D
		if is_instance_valid(pot):
			pot.visible = false
	var glass_node:=safe.find_child("Safe_glass",true,false) as MeshInstance3D'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("ceramic pots hidden in the safehouse")
