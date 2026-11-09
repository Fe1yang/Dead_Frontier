import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# queue the pieces the first in-game second still compiles: the survivor rigs and every weapon
old_queue = '''	for k in ["medkit","armor","helmet","ammo","grenade","flashbang","launcher","fire_round","coin","silver_coin"]:
		warmup_queue.append("pickup:"+k)
	warmup_queue.append("effects")'''
new_queue = '''	for k in ["medkit","armor","helmet","ammo","grenade","flashbang","launcher","fire_round","coin","silver_coin"]:
		warmup_queue.append("pickup:"+k)
	# survivor rigs and the held weapons: their skin pipelines used to compile on the first
	# frame of the run, which is the stutter right after the loading bar disappears
	for c in (load("res://scripts/lobby_scene_3d.gd") as GDScript).CHARACTERS:
		warmup_queue.append("actor:"+String(c.asset))
	for w in ["pistol","makarov","suomi","smg","shotgun","sniper","rifle","launcher","flame"]:
		warmup_queue.append("weapon:"+w)
	warmup_queue.append("crate")
	warmup_queue.append("barrel")
	warmup_queue.append("effects")'''
assert t.count(old_queue) == 1
t = t.replace(old_queue, new_queue, 1)

# handle the new kinds
old_handle = '''	elif item.begins_with("pickup:"):
		n=PickupScript.new(); n.kind=item.trim_prefix("pickup:"); warmup_root.add_child(n)'''
new_handle = '''	elif item.begins_with("pickup:"):
		n=PickupScript.new(); n.kind=item.trim_prefix("pickup:"); warmup_root.add_child(n)
	elif item.begins_with("actor:"):
		var path: String = item.trim_prefix("actor:")
		if ResourceLoader.exists(path):
			n = (load(path) as PackedScene).instantiate() as Node3D
			if n != null: warmup_root.add_child(n)
	elif item.begins_with("weapon:"):
		var wid: String = item.trim_prefix("weapon:").to_upper()
		var wpath := "res://assets/models/weapons/%s.glb" % wid.to_lower()
		if wid == "RIFLE": wpath = "res://assets/models/rifle.glb"
		if ResourceLoader.exists(wpath):
			n = (load(wpath) as PackedScene).instantiate() as Node3D
			if n != null: warmup_root.add_child(n)
	elif item == "crate":
		n = WeaponCrateScript.new(); warmup_root.add_child(n); n.setup("SMG", 3)
	elif item == "barrel":
		n = BarrelScript.new(); warmup_root.add_child(n)'''
assert t.count(old_handle) == 1
t = t.replace(old_handle, new_handle, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("warm-up now covers survivor rigs, weapons, crates and barrels")
