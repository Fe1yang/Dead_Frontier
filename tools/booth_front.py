import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The station sits in a recess of the facade, so the booth at its centre line ended up INSIDE the
# building. Stand it in front of the station instead, on the walkway side, facing the road.
old = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# clear of the station along the street, on the same pavement line
	var z: float = shel.end.z + 1.4 if side < 0.0 else shel.position.z - 1.4
	var x: float = shel.get_center().x
	_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)'''
new = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# in front of the station, towards the road: its own x line is inside the building recess
	var x: float = (shel.position.x - 0.85) if side > 0.0 else (shel.end.x + 0.85)
	var z: float = shel.get_center().z
	_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("booth moved in front of the station, towards the road")
