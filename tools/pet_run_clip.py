import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pet_companion_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if anim and anim.is_playing():
		anim.stop(); (gallop.sk as Skeleton3D).reset_bone_poses()
	if gallop:'''
new = '''	# Every four legged pet runs on the rig's own run cycle: the baked clip reads as a real
	# gallop, the procedural version only wiggled the legs in place.
	if anim and anim.has_animation("Dog_Run"):
		if anim.current_animation != "Dog_Run" or not anim.is_playing():
			anim.play("Dog_Run", 0.15)
		anim.speed_scale = 1.0
		return
	if anim and anim.is_playing():
		anim.stop(); (gallop.sk as Skeleton3D).reset_bone_poses()
	if gallop:'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pets play the baked Dog_Run cycle")
