import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# sit the vest on the chest (about 1.2 m up a 1.75 m survivor) and follow the spine bone so it
# stops floating when the torso leans
old = '''		# sit the shell over the chest: half its height up from the feet
		armor_model.position.y = 1.05
		model.add_child(armor_model)'''
new = '''		# hang it off the chest bone when the rig has one, so it leans with the torso
		var spine_idx: int = skeleton.find_bone("spine_02") if is_instance_valid(skeleton) else -1
		if spine_idx < 0 and is_instance_valid(skeleton):
			spine_idx = skeleton.find_bone("spine_01")
		if spine_idx >= 0:
			var anchor := BoneAttachment3D.new()
			anchor.bone_name = skeleton.get_bone_name(spine_idx)
			skeleton.add_child(anchor)
			anchor.add_child(armor_model)
			armor_model.position = Vector3(0.0, 0.02, 0.0)
		else:
			armor_model.position.y = 1.20
			model.add_child(armor_model)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# a slightly narrower shell sits inside the shoulders instead of swallowing them
t = t.replace("\t\t\t\tarmor_model.scale = Vector3.ONE * (0.62 / widest)",
              "\t\t\t\tarmor_model.scale = Vector3.ONE * (0.56 / widest)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armour is bound to the chest bone and sized to 0.56 m")
