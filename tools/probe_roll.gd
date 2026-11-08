extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _top_z(node: Node3D) -> float:
	var best := -1.0e9
	var best_z := 0.0
	for mi in node.find_children("*", "MeshInstance3D", true, false):
		var m: MeshInstance3D = mi
		if m.mesh == null: continue
		var arrays = m.mesh.surface_get_arrays(0)
		var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		for v in verts:
			var w: Vector3 = m.global_transform * v
			if w.y > best:
				best = w.y; best_z = w.z
	return best_z
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	main.set("owned_vehicle", ""); main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(0.35).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9); main.set("barrel_timer", 1.0e9)
	main.call("_spawn_rollers")
	await create_timer(0.3).timeout
	var r = null
	for q in (main.get("crates") as Array):
		if is_instance_valid(q) and q.has_method("is_roller"): r = q
	if r == null:
		print("no roller"); quit(); return
	r.position = Vector3(0.0, 0.0, -12.0)
	await create_timer(0.05).timeout
	var z0: float = r.position.z
	var tz0: float = _top_z(r)
	await create_timer(0.25).timeout
	var z1: float = r.position.z
	var tz1: float = _top_z(r)
	print("BARREL pos dz=", snappedf(z1 - z0, 0.001), "  top-surface dz=", snappedf(tz1 - tz0, 0.001))
	print("(+z = toward the player/camera: both numbers must be positive for a forward roll)")
	print("ROLL_DONE")
	quit()
