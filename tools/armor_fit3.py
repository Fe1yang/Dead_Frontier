import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

start = t.find("\t\t# hang it off the chest bone when the rig has one")
assert start > 0
end = t.find("\n", t.find("\t\t\tmodel.add_child(armor_model)", start))
assert end > start

new = '''		# Parented to the body, not a bone: the vest model's own origin is mid-chest, so a bone
		# attachment put it around the head. Measured fit: 0.46 m wide, centred 1.12 m up.
		armor_model.scale = Vector3.ONE * (0.46 / widest)
		armor_model.rotation.y = PI          # the GLB faces backwards
		armor_model.position = Vector3(0.0, 1.12, 0.0)
		model.add_child(armor_model)'''
t = t[:start] + new + t[end:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armour re-parented to the body at 1.12 m, 0.46 m wide, facing forward")
