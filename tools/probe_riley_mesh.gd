extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var path := "res://assets/models/actors/survivor_riley_universal.glb"
	print("exists=", ResourceLoader.exists(path))
	var s = load(path).instantiate()
	root.add_child(s)
	await process_frame
	var box := AABB(); var first := true
	for mi in s.find_children("*", "MeshInstance3D", true, false):
		var m: MeshInstance3D = mi
		if m.mesh == null: continue
		var b: AABB = m.global_transform * m.get_aabb()
		box = b if first else box.merge(b)
		first = false
		print("MESH ", m.name, " skinned=", m.skin != null, " aabb_size=", b.size)
	print("TOTAL aabb=", box, " root_scale=", s.scale)
	print("RILEYMESH_DONE")
	quit()
