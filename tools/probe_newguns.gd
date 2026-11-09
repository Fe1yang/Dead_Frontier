extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	for n in ["makarov", "molotov", "pipe_bomb", "grenade.fbx"]:
		var p: String = "res://assets/models/weapons/%s.glb" % n
		if not ResourceLoader.exists(p):
			print(n, " MISSING"); continue
		var s := (load(p) as PackedScene).instantiate() as Node3D
		root.add_child(s)
		await process_frame
		var box := AABB(); var first := true
		for m in s.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		var mats := 0
		for m in s.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh: mats += mi.mesh.get_surface_count()
		print(n, " size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)), " surfaces=", mats)
		s.queue_free()
	print("NG_DONE")
	quit()
