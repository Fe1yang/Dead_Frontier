import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if weapon == "FLAME" and is_instance_valid(weapon_model):'''
new = '''	# Any weapon: the barrel tip is the point of its own bounding box furthest along the aim, so
	# long guns (the sniper and the rifle put bullets beside the left hand) line up correctly.
	if is_instance_valid(weapon_model):'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

old_tail = '''	if is_instance_valid(weapon_model):
		var pt: Vector3=MUZZLE_POINTS.get(weapon,MUZZLE_POINTS["PISTOL"])
		if weapon_flipped: pt=Vector3(-pt.x,pt.y,-pt.z)
		return weapon_model.to_global(pt)
'''
new_tail = '''	if is_instance_valid(weapon_model):
		var pt: Vector3=MUZZLE_POINTS.get(weapon,MUZZLE_POINTS["PISTOL"])
		if weapon_flipped: pt=Vector3(-pt.x,pt.y,-pt.z)
		return weapon_model.to_global(pt)
'''
assert t.count(old_tail) == 1

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("muzzle_position now uses the weapon bounds for every gun")
