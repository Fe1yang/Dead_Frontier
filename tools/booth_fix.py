import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# "awning" matched the shop awning, whose bounds straddle the whole street: its centre is x~0,
# which is exactly why the booth landed in the middle of the road.
old_hints = 'const SHELTER_HINTS := ["shelter", "bus", "awning", "kiosk", "stand", "canopy"]'
new_hints = 'const SHELTER_HINTS := ["shelter", "busstop", "bus_stop", "bus", "kiosk"]'
assert t.count(old_hints) == 1
t = t.replace(old_hints, new_hints, 1)

old_filter = '''		var a: AABB = mi.global_transform * mi.get_aabb()
		if absf(a.position.x) < 4.6:
			continue'''
new_filter = '''		var a: AABB = mi.global_transform * mi.get_aabb()
		# a real shelter sits wholly on one pavement; anything crossing the centre line is not one
		var on_left: bool = a.end.x < -4.6
		var on_right: bool = a.position.x > 4.6
		if not (on_left or on_right):
			continue
		if a.size.x > 4.0 or a.size.y > 4.5:
			continue'''
assert t.count(old_filter) == 1, t.count(old_filter)
t = t.replace(old_filter, new_filter, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("shelter detection no longer matches the shop awning")
