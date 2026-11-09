import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''		if not afirst:
			var widest: float = maxf(abox.size.x, maxf(abox.size.y, abox.size.z))
			if widest > 0.01:
				armor_model.scale = Vector3.ONE * (0.46 / widest)
		armor_model.rotation.y = PI          # the GLB faces backwards
		armor_model.position = Vector3(0.0, 1.12, 0.0)
		model.add_child(armor_model)'''
new = '''		# Put the vest's own centre on the chest: its GLB origin is not centred, which is why a
		# bare position put it around the survivor's head.
		var holder := Node3D.new()
		holder.position = Vector3(0.0, 1.16, 0.0)
		model.add_child(holder)
		if not afirst:
			var widest: float = maxf(abox.size.x, maxf(abox.size.y, abox.size.z))
			if widest > 0.01:
				var sc: float = 0.46 / widest
				armor_model.scale = Vector3.ONE * sc
				armor_model.position = -abox.get_center() * sc
		armor_model.rotation.y = PI          # the GLB faces backwards
		holder.add_child(armor_model)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# helmet: same treatment, centre it on its own box before sitting it on the skull
old_h = "\thelmetscale"
old_helmet = "\t\tvar widest: float = maxf(box.size.x, maxf(box.size.y, box.size.z))\n\t\thelmet_model.scale = Vector3.ONE * (0.34 / widest)\n\t\thelmet_model.position = Vector3(0, 0.030 - box.get_center().y * (0.34 / maxf(widest, 0.001)), 0.010)"
if t.count(old_helmet) == 1:
    new_helmet = '''		var widest: float = maxf(box.size.x, maxf(box.size.y, box.size.z))
		var hs: float = 0.34 / maxf(widest, 0.001)
		helmet_model.scale = Vector3.ONE * hs
		# centre the shell on the head bone instead of on its own raw origin
		helmet_model.position = -box.get_center() * hs + Vector3(0.0, 0.02, 0.0)'''
    t = t.replace(old_helmet, new_helmet, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armour and helmet are centred on their own bounds")
