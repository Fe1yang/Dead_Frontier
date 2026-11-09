import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# re-enable the pothole, but hard-cap how many cones may exist on the road at once
old = '''	# (the pothole-cone pattern was removed: it read as a field of cones on the tarmac)'''
new = '''	if rng.randf()<0.10 and _cone_obstacle_count() < 3:
		_spawn_pothole()
		return'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

old_guard = '''func _spawn_pothole() -> void:
	if true: return  # disabled: cones on the roadway flooded the screen'''
new_guard = '''## How many cone obstacles are on the road right now (used to cap them).
func _cone_obstacle_count() -> int:
	var n := 0
	for o in obstacles:
		if is_instance_valid(o) and String(o.kind) == "cone":
			n += 1
	return n


func _spawn_pothole() -> void:'''
assert t.count(old_guard) == 1, t.count(old_guard)
t = t.replace(old_guard, new_guard, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pothole back at 10% with a hard cap of 3 cones on the road")
