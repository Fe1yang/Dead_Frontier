import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) delete the decorative cone builder and its helpers
start = t.find("## Orange traffic cone: replaces the manhole covers")
end = t.find("func _prop_node(", start)
assert start > 0 and end > start, (start, end)
t = t[:start] + t[end:]

# 2) drop the crater ring block
ring_start = t.find("\t\t# ring of 3..6 cones around the crater mouth, evenly spaced with a little jitter")
if ring_start > 0:
    ring_end = t.find("\tif rng_d.randf() < 0.14:", ring_start)
    assert ring_end > ring_start
    t = t[:ring_start] + t[ring_end:]

# 3) drop the pavement decoration cone
pav = t.find("\t\t_traffic_cone(road, Vector3(side * decor_rng.randf_range(8.45, 12.0)")
if pav > 0:
    line_end = t.find("\n", pav)
    # also remove the comment line above it
    prev_nl = t.rfind("\n", 0, pav)
    prev_line_start = t.rfind("\n", 0, prev_nl) + 1
    if "manholes sit along the pavement line" in t[prev_line_start:prev_nl]:
        t = t[:prev_line_start] + t[line_end + 1:]
    else:
        t = t[:pav] + t[line_end + 1:]

# 4) one clean spawner: the game's own cone obstacle, at most three alive, never stacking
old_pattern = "\tif rng.randf()<0.10 and _cone_obstacle_count() < 3:\n\t\t_spawn_pothole()\n\t\treturn"
if old_pattern not in t:
    old_pattern = "\t# (the pothole-cone pattern was removed: it read as a field of cones on the tarmac)"
new_pattern = '''\tif rng.randf()<0.12 and _cone_obstacle_count() == 0:
\t\t_spawn_cone_triangle()
\t\treturn'''
assert t.count(old_pattern) == 1, t.count(old_pattern)
t = t.replace(old_pattern, new_pattern, 1)

# 5) replace the old pothole body with a tight triangle that never exceeds three cones
pothole_start = t.find("## A pothole marked by three cones.")
if pothole_start < 0:
    pothole_start = t.find("func _spawn_pothole() -> void:")
pothole_end = t.find("func _spawn_obstacle_pattern()", pothole_start)
assert pothole_start > 0 and pothole_end > pothole_start

new_body = '''## A pothole marked by three cones in a tight triangle. Only ever spawned when the road has no
## cones on it at all, so a run can never accumulate more than three.
func _spawn_cone_triangle() -> void:
	var lane_x: float = [-2.0, 0.0, 2.0][rng.randi_range(0, 2)]
	var z := -46.0
	for off in [Vector3(-0.7, 0, 0.5), Vector3(0.7, 0, 0.5), Vector3(0, 0, -0.6)]:
		_spawn_obstacle("cone", lane_x + off.x, z + off.z)


'''
t = t[:pothole_start] + new_body + t[pothole_end:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("cone code rewritten: decoration removed, capped triangle spawner in place")
print("remaining _traffic_cone refs:", t.count("_traffic_cone"))
