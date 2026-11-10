import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\gate_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "_mesh_cache" not in t:
    anchor = "static var _shared:={}"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + '''
## Shared mesh resources. Building a gate used to allocate ~17 new meshes, and every new mesh is
## uploaded to the GPU on first use, which is what the gate frame cost.
static var _mesh_cache:={}


static func _box_mesh(size: Vector3) -> BoxMesh:
	var key := "b|%.2f|%.2f|%.2f" % [size.x, size.y, size.z]
	var m: BoxMesh = _mesh_cache.get(key, null) as BoxMesh
	if m == null:
		m = BoxMesh.new(); m.size = size; _mesh_cache[key] = m
	return m


static func _cyl_mesh(top_r: float, bottom_r: float, h: float) -> CylinderMesh:
	var key := "c|%.2f|%.2f|%.2f" % [top_r, bottom_r, h]
	var m: CylinderMesh = _mesh_cache.get(key, null) as CylinderMesh
	if m == null:
		m = CylinderMesh.new(); m.top_radius = top_r; m.bottom_radius = bottom_r; m.height = h
		_mesh_cache[key] = m
	return m


static func _sphere_mesh(r: float, h: float, segs := 0, rings := 0) -> SphereMesh:
	var key := "s|%.2f|%.2f|%d|%d" % [r, h, segs, rings]
	var m: SphereMesh = _mesh_cache.get(key, null) as SphereMesh
	if m == null:
		m = SphereMesh.new(); m.radius = r; m.height = h
		if segs > 0: m.radial_segments = segs
		if rings > 0: m.rings = rings
		_mesh_cache[key] = m
	return m''', 1)

# _box uses the shared mesh
old_box = '''	var n:=MeshInstance3D.new(); var mesh:=BoxMesh.new(); mesh.size=size; n.mesh=mesh
	n.position=pos; n.material_override=mat; parent.add_child(n); return n'''
new_box = '''	var n:=MeshInstance3D.new(); n.mesh=_box_mesh(size)
	n.position=pos; n.material_override=mat; parent.add_child(n); return n'''
assert t.count(old_box) == 1, t.count(old_box)
t = t.replace(old_box, new_box, 1)

# posts
old_post = '''	var n:=MeshInstance3D.new(); var c:=CylinderMesh.new(); c.top_radius=0.09; c.bottom_radius=0.11; c.height=POST_HEIGHT
	n.mesh=c; n.position=Vector3(x,POST_HEIGHT*0.5,0); n.material_override=post_mat; add_child(n)
	var cap:=MeshInstance3D.new(); var s:=SphereMesh.new(); s.radius=0.13; s.height=0.26; cap.mesh=s
	cap.position=Vector3(x,POST_HEIGHT,0); cap.material_override=post_mat; add_child(cap)
	var foot:=MeshInstance3D.new(); var f:=CylinderMesh.new(); f.top_radius=0.16; f.bottom_radius=0.2; f.height=0.1
	foot.mesh=f; foot.position=Vector3(x,0.05,0); foot.material_override=post_mat; add_child(foot)'''
new_post = '''	var n:=MeshInstance3D.new(); n.mesh=_cyl_mesh(0.09, 0.11, POST_HEIGHT)
	n.position=Vector3(x,POST_HEIGHT*0.5,0); n.material_override=post_mat; add_child(n)
	var cap:=MeshInstance3D.new(); cap.mesh=_sphere_mesh(0.13, 0.26)
	cap.position=Vector3(x,POST_HEIGHT,0); cap.material_override=post_mat; add_child(cap)
	var foot:=MeshInstance3D.new(); foot.mesh=_cyl_mesh(0.16, 0.2, 0.1)
	foot.position=Vector3(x,0.05,0); foot.material_override=post_mat; add_child(foot)'''
assert t.count(old_post) == 1, t.count(old_post)
t = t.replace(old_post, new_post, 1)

# legendary spark mesh
old_spark = '''		var spark_mesh:=SphereMesh.new(); spark_mesh.radius=0.5; spark_mesh.height=1.0; spark_mesh.radial_segments=6; spark_mesh.rings=3'''
new_spark = '''		var spark_mesh := _sphere_mesh(0.5, 1.0, 6, 3)'''
assert t.count(old_spark) == 1
t = t.replace(old_spark, new_spark, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("gate meshes are shared")
