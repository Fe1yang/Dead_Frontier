extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var dir := "res://assets/models/lobby_psx/"
	for n in ["floorWood","wallPlaster","ceilingPlaster","couchBig","table","tv","shelves","carpet","windowCurtains","wallDoorPlaster"]:
		var p: String = dir + n + ".glb"
		if not ResourceLoader.exists(p):
			print(n, " MISSING")
			continue
		var s := (load(p) as PackedScene).instantiate() as Node3D
		root.add_child(s)
		await process_frame
		var box := AABB(); var first := true
		for m in s.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print(n, " size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)), " min=", Vector3(snappedf(box.position.x,0.01), snappedf(box.position.y,0.01), snappedf(box.position.z,0.01)))
		s.queue_free()
	print("PSX_DONE")
	quit()
