import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# ---- the cone becomes a road obstacle kind ---------------------------------------------------
po = base + r"\road_obstacle_3d.gd"
p = io.open(po, encoding="utf-8").read()

if 'kind=="cone"' not in p:
    anchor = '\telif kind=="police":'
    assert p.count(anchor) == 1
    branch = '''	elif kind=="cone":
		# a pothole marker: small, so it never blocks a lane on its own
		half_extents=Vector2(0.22,0.22)
		damage=8.0
		var cone_packed: Resource=load("res://assets/models/props/traffic_cone.glb")
		if cone_packed!=null:
			var cone:=cone_packed.instantiate() as Node3D
			if cone!=null:
				cone.position=Vector3(0,0,0)
				model.add_child(cone)
		# the hole itself: a dark disc so the cones read as a warning, not random clutter
		var disc:=MeshInstance3D.new()
		var cyl:=CylinderMesh.new(); cyl.top_radius=0.55; cyl.bottom_radius=0.55; cyl.height=0.02
		var dm:=StandardMaterial3D.new(); dm.albedo_color=Color(0.05,0.05,0.055); dm.roughness=0.95
		cyl.material=dm; disc.mesh=cyl; disc.position=Vector3(0,0.012,0)
		model.add_child(disc)
'''
    p = p.replace(anchor, branch + anchor, 1)
    io.open(po, "w", encoding="utf-8", newline="\n").write(p)
    print("road_obstacle_3d: cone kind added")

# ---- a spawn pattern that rings a pothole without closing the road ----------------------------
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()

if "_spawn_pothole" not in m:
    helper = '''## A pothole marked by three cones. It always leaves the other lanes open: the cluster is
## 3.4 m wide at most, and the road is 7.2 m.
func _spawn_pothole() -> void:
	var lane_x: float = [-2.0, 0.0, 2.0][rng.randi_range(0, 2)]
	var z := -48.0
	var offsets := [Vector3(-0.75, 0, 0.55), Vector3(0.75, 0, 0.55), Vector3(0, 0, -0.75)]
	for off in offsets:
		_spawn_obstacle("cone", lane_x + off.x, z + off.z)


'''
    anchor2 = "func _spawn_obstacle_pattern() -> void:"
    assert m.count(anchor2) == 1
    m = m.replace(anchor2, helper + anchor2, 1)

    # ~1 in 4 patterns is the pothole instead of the usual fare
    old_pat = "func _spawn_obstacle_pattern() -> void:\n"
    assert m.count(old_pat) == 1
    m = m.replace(old_pat, old_pat + "\tif rng.randf()<0.28:\n\t\t_spawn_pothole()\n\t\treturn\n", 1)

    io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
    print("main_3d: pothole pattern added")
