import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The real source of the cone flood: the pothole pattern dropped three cones on the road on 28%
# of obstacle waves. It was invisible as "a pothole" and read as a field of cones.
old = '''	if rng.randf()<0.28:
		_spawn_pothole()
		return'''
new = '''	if rng.randf()<0.04:
		_spawn_pothole()
		return'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# and a pothole gets two cones, not three
old2 = '''	var offsets := [Vector3(-0.75, 0, 0.55), Vector3(0.75, 0, 0.55), Vector3(0, 0, -0.75)]'''
new2 = '''	var offsets := [Vector3(-0.75, 0, 0.55), Vector3(0.75, 0, 0.55)]'''
assert t.count(old2) == 1, t.count(old2)
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pothole cone wave 28% -> 4%, three cones -> two")
