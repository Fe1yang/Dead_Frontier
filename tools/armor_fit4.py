import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		if not afirst:
			var widest: float = maxf(abox.size.x, maxf(abox.size.y, abox.size.z))
			if widest > 0.01:
				armor_model.scale = Vector3.ONE * (0.56 / widest)
		# Parented to the body, not a bone: the vest model's own origin is mid-chest, so a bone
		# attachment put it around the head. Measured fit: 0.46 m wide, centred 1.12 m up.
		armor_model.scale = Vector3.ONE * (0.46 / widest)
		armor_model.rotation.y = PI          # the GLB faces backwards
		armor_model.position = Vector3(0.0, 1.12, 0.0)
		model.add_child(armor_model)'''
new = '''		# Parented to the body, not a bone: the vest model's origin is mid-chest, so a bone
		# attachment put it around the survivor's head. Measured fit: 0.46 m wide, 1.12 m up.
		if not afirst:
			var widest: float = maxf(abox.size.x, maxf(abox.size.y, abox.size.z))
			if widest > 0.01:
				armor_model.scale = Vector3.ONE * (0.46 / widest)
		armor_model.rotation.y = PI          # the GLB faces backwards
		armor_model.position = Vector3(0.0, 1.12, 0.0)
		model.add_child(armor_model)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("widest is declared inside the bounds branch again")
