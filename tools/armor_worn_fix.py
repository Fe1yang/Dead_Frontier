import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		armor_model = load("res://assets/models/armor.glb").instantiate() as Node3D
		# Fit around the torso, not around the character's feet: the source model is
		# modelled at its final height, so scaling needs a compensating vertical offset.
		armor_model.scale = Vector3(0.72, 0.78, 0.64)
		armor_model.position.y = 1.315 * (1.0 - armor_model.scale.y)
		model.add_child(armor_model)'''
new = '''		armor_model = load("res://assets/models/armor.glb").instantiate() as Node3D
		# The vest GLB is authored around 120 m tall, so a fixed factor produced a 30 m vest
		# hanging over the survivor. Normalise it to a 0.62 m wide shell first.
		var abox := AABB()
		var afirst := true
		for m in armor_model.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var a: AABB = mi.get_aabb()
			abox = a if afirst else abox.merge(a)
			afirst = false
		if not afirst:
			var widest: float = maxf(abox.size.x, maxf(abox.size.y, abox.size.z))
			if widest > 0.01:
				armor_model.scale = Vector3.ONE * (0.62 / widest)
		# sit the shell over the chest: half its height up from the feet
		armor_model.position.y = 1.05
		model.add_child(armor_model)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("worn armour normalised to 0.62 m")
