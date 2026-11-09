import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# --- 1) the projectile knows the molotov ---------------------------------------------------
po = io.open(base + r"\ordnance_projectile_3d.gd", encoding="utf-8").read()
if '"molotov"' not in po:
    old = '\t"fire": "res://assets/models/fire_round.glb"'
    assert po.count(old) == 1
    po = po.replace(old, old + ',\n\t"molotov": "res://assets/models/weapons/molotov.glb"', 1)
    old_fuse = '\telif kind in ["launcher", "fire"]: fuse = 2.4'
    assert po.count(old_fuse) == 1
    po = po.replace(old_fuse, old_fuse + '\n\telif kind == "molotov": fuse = 1.7', 1)
    io.open(base + r"\ordnance_projectile_3d.gd", "w", encoding="utf-8", newline="\n").write(po)

# --- 2) throwing and detonating ------------------------------------------------------------
m = io.open(base + r"\main_3d.gd", encoding="utf-8").read()

old_throw = '''	elif kind=="flash":
		if player.flashbang_count<=0: return false
		player.flashbang_count-=1
	else: return false'''
new_throw = '''	elif kind=="flash":
		if player.flashbang_count<=0: return false
		player.flashbang_count-=1
	elif kind=="molotov":
		if player.molotov_count<=0: return false
		player.molotov_count-=1
	else: return false'''
if "molotov_count" not in m:
    assert m.count(old_throw) == 1
    m = m.replace(old_throw, new_throw, 1)

    # detonation: a wide burn, the same ignition the flamethrower applies
    old_det = '''func _detonate_ordnance(projectile: Node3D) -> void:
	var center: Vector3=projectile.position
	var kind: String=projectile.kind'''
    new_det = '''func _detonate_ordnance(projectile: Node3D) -> void:
	var center: Vector3=projectile.position
	var kind: String=projectile.kind
	if kind=="molotov":
		# a burning pool: everything inside catches fire exactly like a flamethrower hit
		sound.play("explosion"); shake=maxf(shake,0.35)
		_burst(center,Color("ff9b35"),30); _fire_spray(center)
		var pool:=EffectScript.new(); pool.position=Vector3(center.x,0.06,center.z)
		pool.life=3.0; pool.total_life=3.0
		add_child(pool); pool.make_shockwave(Color(1.0,0.55,0.15,0.85),4.0); effects.append(pool)
		for z in zombies:
			if is_instance_valid(z) and not z.dead and _flat_distance(z.position,center)<4.5:
				_z_ignite_molotov(z)
		return'''
    assert m.count(old_det) == 1
    m = m.replace(old_det, new_det, 1)

    helper = '''## Molotov burn: identical numbers to the flamethrower so the two feel like one weapon family.
func _z_ignite_molotov(z: Node3D) -> void:
	_hit_zombie(z, FLAME_TICK_DAMAGE, "torso", z.position + Vector3(0, 1.0, 0), Color("ffb14d"))
	z.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)


'''
    anchor = "func _detonate_ordnance(projectile: Node3D) -> void:"
    m = m.replace(anchor, helper + anchor, 1)

io.open(base + r"\main_3d.gd", "w", encoding="utf-8", newline="\n").write(m)
print("molotov projectile + area ignition wired")
