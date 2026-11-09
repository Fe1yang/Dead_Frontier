import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) the flamethrower ends up backwards: the global half-turn that fixes the gun set overshoots it
pp = base + r"\player_3d.gd"
p = io.open(pp, encoding="utf-8").read()
old = '''	weapon_model.rotate_y(PI)
	weapon_flipped = true'''
new = '''	weapon_model.rotate_y(PI)
	# The steampunk flamethrower has its tank behind the receiver, so the muzzle-end heuristic
	# already points the right way and the global half turn puts the nozzle at the shooter.
	if weapon == "FLAME":
		weapon_model.rotate_y(PI)
	weapon_flipped = true'''
assert p.count(old) == 1
p = p.replace(old, new, 1)
io.open(pp, "w", encoding="utf-8", newline="\n").write(p)
print("flame no longer flipped backwards")

# 2) the phone booth must stand side-on with its glass facing the street
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()
old_yaw = '\t_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)'
new_yaw = '\t# side-on, glass towards the road\n\t_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), -side * PI * 0.5)'
assert m.count(old_yaw) == 1
m = m.replace(old_yaw, new_yaw, 1)
io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
print("phone booth turned to face the street")
