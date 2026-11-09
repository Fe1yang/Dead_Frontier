import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "func _cone_obstacle_count" not in t:
    anchor = "func _spawn_cone_triangle() -> void:"
    assert t.count(anchor) == 1, t.count(anchor)
    helper = '''## How many cone obstacles are on the road right now.
func _cone_obstacle_count() -> int:
	var n := 0
	for o in obstacles:
		if is_instance_valid(o) and String(o.kind) == "cone":
			n += 1
	return n


'''
    t = t.replace(anchor, helper + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("_cone_obstacle_count restored")

# cones must cast shadows like every other prop
p2 = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\road_obstacle_3d.gd"
h = io.open(p2, encoding="utf-8").read()
old = '''			if cone!=null:
				cone.position=Vector3(0,0,0)
				model.add_child(cone)'''
new = '''			if cone!=null:
				cone.position=Vector3(0,0,0)
				# the generated cone GLB arrives with shadow casting off
				for mi in cone.find_children("*", "MeshInstance3D", true, false):
					var cm := mi as MeshInstance3D
					if cm != null:
						cm.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
				model.add_child(cone)'''
assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("cone casts a shadow")
