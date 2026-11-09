extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var z = (load("res://scripts/zombie_3d.gd") as GDScript).new()
	root.add_child(z)
	await process_frame
	z.call("configure", "jockey", 1.0)
	await process_frame
	var ap = z.find_child("AnimationPlayer", true, false)
	print("jockey clip=", ap.current_animation if ap else "none", " playing=", ap.is_playing() if ap else false)
	var box = AABB(); var first = true
	for m in z.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		var a: AABB = mi.global_transform * mi.get_aabb()
		box = a if first else box.merge(a); first = false
	print("jockey size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)))
	print("JOCKEY_DONE")
	quit()
