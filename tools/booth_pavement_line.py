import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# in front of the station, towards the road: its own x line is inside the building recess
	var x: float = (shel.position.x - 0.85) if side > 0.0 else (shel.end.x + 0.85)
	var z: float = shel.get_center().z'''
new = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# On the station's own pavement line (x 5.1..6.9), not near the kerb. Pulling it to 4.29 put
	# it on the asphalt edge, which is what read as "in the middle of the road".
	var x: float = shel.get_center().x
	var z: float = shel.end.z + 1.5 if side < 0.0 else shel.position.z - 1.5'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("booth back on the station's pavement line, 1.5 m clear along the street")
