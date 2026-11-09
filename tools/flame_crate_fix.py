import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) items on the crates were huge: back to a modest bump
cp = base + r"\weapon_crate_3d.gd"
c = io.open(cp, encoding="utf-8").read()
assert "const ITEM_BOOST := 2.4" in c
c = c.replace("const ITEM_BOOST := 2.4", "const ITEM_BOOST := 1.15", 1)
io.open(cp, "w", encoding="utf-8", newline="\n").write(c)
print("crate item boost -> 1.15")

# 2) the flamethrower: bring the jet back, and let the cone burn crates and barrels so auto-fire
#    breaks them like the guns do
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()

old = '''	player.fire()
	# The particle jet is parked until it can be tested on device: on screen it covered the
	# camera in a red wash. Damage and sound are unaffected.
	sound.play("flame")'''
new = '''	player.fire()
	player.pulse_flame()
	# the cone also cooks whatever drop is in it, so auto-fire breaks crates and barrels
	for crate in crates:
		if not is_instance_valid(crate) or crate.is_queued_for_deletion():
			continue
		var cd: Vector3 = crate.global_position - origin
		cd.y = 0.0
		if cd.length() > FLAME_RANGE:
			continue
		if cd.length() > 0.4 and flat_fwd.dot(cd.normalized()) < cos(deg_to_rad(FLAME_HALF_ANGLE)):
			continue
		crate.take_hit()
		hit += 1
	for barrel in barrels:
		if not is_instance_valid(barrel) or barrel.is_queued_for_deletion():
			continue
		var bd: Vector3 = barrel.global_position - origin
		bd.y = 0.0
		if bd.length() > FLAME_RANGE:
			continue
		if bd.length() > 0.4 and flat_fwd.dot(bd.normalized()) < cos(deg_to_rad(FLAME_HALF_ANGLE)):
			continue
		barrel.take_hit()
		hit += 1
	sound.play("flame")'''
assert m.count(old) == 1, m.count(old)
m = m.replace(old, new, 1)

io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
print("flame jet restored; cone now breaks crates and barrels")
