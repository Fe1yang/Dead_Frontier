extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	for idx in [2, 3, 5]:
		var road = (main.get("roads") as Array)[idx]
		print("--- district ", idx)
		for m in road.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			var on_side: bool = (a.position.x > 4.6) or (a.end.x < -4.6)
			if not on_side: continue
			if a.size.x < 0.8 or a.size.x > 6.0: continue
			if a.size.y < 1.5 or a.size.y > 4.0: continue
			if a.size.z < 0.8 or a.size.z > 6.0: continue
			print("   ", mi.name, " x=", snappedf(a.position.x,0.1), "..", snappedf(a.end.x,0.1),
				" y=", snappedf(a.position.y,0.1), "..", snappedf(a.end.y,0.1),
				" z=", snappedf(a.position.z,0.1), "..", snappedf(a.end.z,0.1))
	print("BX2_DONE")
	quit()
