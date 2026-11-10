import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# falloff shared by every target in the cone
if "func _flame_falloff" not in t:
    helper = '''## A jet loses heat with distance: point blank burns hard, the far end of the cone only singes.
func _flame_falloff(dist: float) -> float:
	var t: float = clampf(1.0 - dist / maxf(0.1, FLAME_RANGE), 0.0, 1.0)
	return lerpf(0.22, 1.0, pow(t, 1.4))


'''
    anchor = "func _fire_flame() -> bool:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

old_z = '''		_hit_zombie(z, FLAME_TICK_DAMAGE, "torso", z.position + Vector3(0, 1.0, 0), Color("ffb14d"))
		z.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)'''
new_z = '''		var heat: float = _flame_falloff(dist)
		_hit_zombie(z, FLAME_TICK_DAMAGE * heat, "torso", z.position + Vector3(0, 1.0, 0), Color("ffb14d"))
		z.ignite(FLAME_BURN_SECONDS * lerpf(0.5, 1.0, heat), z.max_health * FLAME_BURN_FRACTION * heat)'''
assert t.count(old_z) == 1, t.count(old_z)
t = t.replace(old_z, new_z, 1)

# crates and barrels take the same falloff so the cone reads consistently
old_c = '''		if crate.take_hit(FLAME_STRUCTURE_HITS):'''
new_c = '''		if crate.take_hit(maxf(1.0, FLAME_STRUCTURE_HITS * _flame_falloff(cd.length()))):'''
assert t.count(old_c) == 1
t = t.replace(old_c, new_c, 1)

old_b = '''		if barrel.take_hit(400.0):'''
new_b = '''		if barrel.take_hit(400.0 * _flame_falloff(bd.length())):'''
assert t.count(old_b) == 1
t = t.replace(old_b, new_b, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("flame damage now falls off with distance")
