import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The station in the district model is CITY_station_frame / CITY_station_glass (a box on the
# pavement, x 5.1..6.9, z 21.9..26.4). Match that.
old_hints = 'const SHELTER_HINTS := ["shelter", "busstop", "bus_stop", "bus", "kiosk"]'
new_hints = 'const SHELTER_HINTS := ["station", "shelter", "busstop", "bus_stop", "kiosk"]'
assert t.count(old_hints) == 1
t = t.replace(old_hints, new_hints, 1)

# place the booth just beyond the station along the street, sharing its pavement line
old_place = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# same x line as the shelter, 2.6 m along the street, so neither can overlap the other
	var z := shel.get_center().z + 2.6 * (-1.0 if side < 0.0 else 1.0)
	var x := shel.get_center().x
	_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)'''
new_place = '''	var side := -1.0 if shel.get_center().x < 0.0 else 1.0
	# clear of the station along the street, on the same pavement line
	var z: float = shel.end.z + 1.4 if side < 0.0 else shel.position.z - 1.4
	var x: float = shel.get_center().x
	_prop_node("phone_booth", road, Vector3(x, PAVEMENT_Y, z), side * PI * 0.5)'''
assert t.count(old_place) == 1, t.count(old_place)
t = t.replace(old_place, new_place, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("booth now aligns with CITY_station_frame")
