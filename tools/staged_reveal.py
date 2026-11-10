import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "REVEAL_BAND" not in t:
    anchor = "const ROAD_SEGMENT:=16.0"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '''
## Street props pop in over a few frames instead of appearing all at once: one district entering
## view used to add 300 draw calls in a single frame, which is what the 180-260 ms spikes were.
const REVEAL_BAND_NEAR := -68.0
const REVEAL_BAND_FAR := -60.0
const REVEAL_PER_FRAME := 10''', 1)

if "func _stage_district_reveal" not in t:
    helper = '''## Hide the optional props of a district that is about to enter the view; they are shown again
## a few at a time by _tick_district_reveal().
func _stage_district_reveal(road: Node3D) -> void:
	var items: Array = []
	for child in road.get_children():
		var nm := String(child.name)
		if nm.begins_with("phone_booth") or nm.begins_with("bench") or nm.begins_with("trash_") \
			or nm.begins_with("manhole") or nm.begins_with("hydrant") or nm.begins_with("can_") \
			or nm.begins_with("lamp"):
			if child is Node3D and (child as Node3D).visible:
				(child as Node3D).visible = false
				items.append(child)
	if items.is_empty():
		return
	road.set_meta("reveal_items", items)
	reveal_jobs.append(road)


## Called once per frame: bring back a handful of props on each district that is still revealing.
func _tick_district_reveal() -> void:
	for road in reveal_jobs.duplicate():
		var items: Array = road.get_meta("reveal_items", [])
		var shown := 0
		while seen_reveal < REVEAL_PER_FRAME and not items.is_empty():
			var node = items.pop_back()
			if is_instance_valid(node):
				(node as Node3D).visible = true
			seen_reveal += 1
			shown += 1
		if items.is_empty():
			reveal_jobs.erase(road)
			road.remove_meta("reveal_items")


'''
    anchor2 = "func _build_district(i: int) -> void:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, helper + anchor2, 1)

# state
if "var reveal_jobs" not in t:
    anchor3 = "var district_cache:={}"
    if t.count(anchor3) != 1:
        anchor3 = "var district_cache := {}"
    assert t.count(anchor3) == 1
    t = t.replace(anchor3, anchor3 + "\nvar reveal_jobs: Array=[]\nvar seen_reveal:=0", 1)

# trigger per frame in the road loop
old_loop = '''	for road in roads:
		road.position.z+=world_speed*delta
		if road.position.z>ROAD_BEHIND+ROAD_SEGMENT:'''
new_loop = '''	for road in roads:
		road.position.z+=world_speed*delta
		var rz: float = road.position.z
		if rz > REVEAL_BAND_NEAR and rz <= REVEAL_BAND_FAR + 0.01 and not road.has_meta("reveal_items"):
			_stage_district_reveal(road)
		if road.position.z>ROAD_BEHIND+ROAD_SEGMENT:'''
assert t.count(old_loop) == 1, t.count(old_loop)
t = t.replace(old_loop, new_loop, 1)

# drain the reveal queue right after the loop
old_after = '''	_tick_lightning(delta)'''
new_after = '''	seen_reveal = 0
	_tick_district_reveal()
	_tick_lightning(delta)'''
assert t.count(old_after) == 1
t = t.replace(old_after, new_after, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("street props now reveal over several frames")
