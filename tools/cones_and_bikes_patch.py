import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) motorcycles on pedestals and barrels: 2.5x bigger
p = ROOT + r"\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()
for key in ("BIKE", "SPORT", "CRUISER"):
    old = '"%s":0.62' % key
    if t.count(old) == 1:
        t = t.replace(old, '"%s":1.55' % key, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("bike preview scale 0.62 -> 1.55")

# 2) manholes become traffic cones ringing the crater
p2 = ROOT + r"\scripts\main_3d.gd"
h = io.open(p2, encoding="utf-8").read()

if "func _traffic_cone" not in h:
    anchor = "func _prop_node(name: String, parent: Node3D, world_pos: Vector3, yaw: float = 0.0) -> Node3D:"
    assert h.count(anchor) == 1
    helper = '''## Orange traffic cone: replaces the manhole covers, which were spawning three deep on the
## tarmac. Cones ring the missile crater instead of trying to fence it perfectly.
func _traffic_cone(parent: Node3D, world_pos: Vector3) -> Node3D:
	var root := Node3D.new()
	parent.add_child(root)
	root.global_position = Vector3(world_pos.x, PAVEMENT_Y, world_pos.z)
	var cone := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0.02
	mesh.bottom_radius = 0.20
	mesh.height = 0.62
	mesh.radial_segments = 10
	mesh.rings = 0
	cone.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color("e8631b")
	mat.roughness = 0.75
	cone.material_override = mat
	cone.position.y = 0.31
	root.add_child(cone)
	var base := MeshInstance3D.new()
	var base_mesh := BoxMesh.new()
	base_mesh.size = Vector3(0.46, 0.06, 0.46)
	base.mesh = base_mesh
	var base_mat := StandardMaterial3D.new()
	base_mat.albedo_color = Color("d2551a")
	base_mat.roughness = 0.8
	base.material_override = base_mat
	base.position.y = 0.03
	root.add_child(base)
	return root


'''
    h = h.replace(anchor, helper + anchor, 1)

# pavement pass: cone instead of a manhole cover
old_pav = '_prop_node("manhole", road, Vector3(side * 8.85 + decor_rng.randf_range(-0.15, 0.15), PAVEMENT_Y + 0.01, base_z + decor_rng.randf_range(-6.0, 6.0)), 0.0)'
if h.count(old_pav) == 1:
    h = h.replace(old_pav, '_traffic_cone(road, Vector3(side * 8.45, PAVEMENT_Y, base_z + decor_rng.randf_range(-6.0, 6.0)))', 1)

# road pass: instead of a cover on the tarmac, ring the crater with cones
old_road = '_prop_node("manhole", road, Vector3(mx, PAVEMENT_Y + 0.01, base_z + rng_d.randf_range(-6.5, 6.5)), 0.0)'
if h.count(old_road) == 1:
    h = h.replace(old_road, '''# ring the crater mouth instead of dropping covers on the tarmac
		for k in range(3):
			var ang := TAU * float(k) / 3.0 + rng_d.randf_range(-0.25, 0.25)
			_traffic_cone(road, Vector3(CRATER_X + cos(ang) * (CRATER_RADIUS + 0.55), PAVEMENT_Y,
				base_z + sin(ang) * (CRATER_RADIUS + 0.55)))''', 1)

io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("manholes replaced by cones around the crater")
