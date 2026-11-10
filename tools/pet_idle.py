import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pet_companion_3d.gd"
t = io.open(P, encoding="utf-8").read()

# remember whether the animal is actually moving this frame
if "var is_moving" not in t:
    anchor = "var yaw_offset := 0.0"
    assert t.count(anchor) == 1
    t = t.replace(anchor, "var is_moving := false   # drives idle vs run clip selection\n" + anchor, 1)

old_step = '''		position+=flat_delta.normalized()*minf(distance,speed*delta)
		position.x=clampf(position.x,-3.25,3.25)
		position.y=0.0'''
new_step = '''		is_moving = distance > 0.12
		position+=flat_delta.normalized()*minf(distance,speed*delta)
		position.x=clampf(position.x,-3.25,3.25)
		position.y=0.0'''
assert t.count(old_step) == 1, t.count(old_step)
t = t.replace(old_step, new_step, 1)

# clearing the flag when biting close range
old_bite = '''		if cooldown<=0.0:'''
new_bite = '''		is_moving = false
		if cooldown<=0.0:'''
assert t.count(old_bite) == 1
t = t.replace(old_bite, new_bite, 1)

# clip selection: idle when standing, run while moving, per-breed names
old_clip = '''	if anim and anim.has_animation("Dog_Run"):
		if anim.current_animation != "Dog_Run" or not anim.is_playing():
			anim.play("Dog_Run", 0.15)
		anim.speed_scale = 1.0
		return'''
new_clip = '''	if anim:
		var idle := _first_clip(anim, ["Dog_Idle", "Lion_Idle", "Tiger_Idle", "Idle", "idle"])
		var run := _first_clip(anim, ["Dog_Run", "Lion_Run", "Tiger_Run", "Run", "run"])
		var want := "" if is_moving else idle
		if want == "":
			want = run
		if want != "":
			if anim.current_animation != want or not anim.is_playing():
				anim.play(want, 0.15)
			anim.speed_scale = 1.0
			return'''
assert t.count(old_clip) == 1, t.count(old_clip)
t = t.replace(old_clip, new_clip, 1)

# helper
if "func _first_clip" not in t:
    helper = '''## First animation name from `names` that this model actually has.
func _first_clip(player: AnimationPlayer, names: Array) -> String:
	for n in names:
		if player.has_animation(String(n)):
			return String(n)
	return ""


'''
    anchor2 = "func _animate(delta: float) -> void:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, helper + anchor2, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("pets now play an idle clip when standing and a run clip when moving")
