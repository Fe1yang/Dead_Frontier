import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The pothole pattern is the only place that drops cones onto the roadway, and it kept showing up
# as a field of them regardless of the rate. Drop the pattern entirely: cones now only exist as
# decoration (crater ring and the rare pavement one).
old = '''	if rng.randf()<0.04:
		_spawn_pothole()
		return'''
new = '''	# (the pothole-cone pattern was removed: it read as a field of cones on the tarmac)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# and stop it firing from anywhere else
old_call = '''func _spawn_pothole() -> void:'''
new_call = '''func _spawn_pothole() -> void:
	if true: return  # disabled: cones on the roadway flooded the screen'''
assert t.count(old_call) == 1
t = t.replace(old_call, new_call, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("roadway cone pattern disabled")
