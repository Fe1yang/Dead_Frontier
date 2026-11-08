extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var scene = load("res://assets/models/armor.glb")
	print("LOADED=", scene != null)
	var inst = scene.instantiate()
	root.add_child(inst)
	await process_frame
	var box = AABB(); var first = true; var meshes = 0
	for m in inst.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		meshes += 1
		var a: AABB = mi.global_transform * mi.get_aabb()
		box = a if first else box.merge(a); first = false
	print("MESHES=", meshes, " size=", box.size, " pos=", box.position)
	print("ARMOR_DONE")
	quit()
