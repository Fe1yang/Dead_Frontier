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
	var road = (main.get("roads") as Array)[3]
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		var nm := String(mi.name).to_lower()
		if nm.find("shelter") != -1 or nm.find("bus") != -1 or nm.find("stop") != -1 or nm.find("bench") != -1:
			var a: AABB = mi.global_transform * mi.get_aabb()
			print(nm, " x=", snappedf(a.position.x,0.1), "..", snappedf(a.end.x,0.1), " z=", snappedf(a.position.z,0.1), "..", snappedf(a.end.z,0.1))
	print("SH_DONE")
	quit()
