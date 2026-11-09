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
	for key in ["asphalt", "pavement", "curb"]:
		var lo := 1.0e9; var hi := -1.0e9; var ylo := 1.0e9
		for m in road.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			if String(mi.name).to_lower().find(key) == -1: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			lo = minf(lo, a.position.x); hi = maxf(hi, a.end.x)
			ylo = minf(ylo, a.position.y)
		if lo < 1.0e9:
			print(key, " x=", snappedf(lo,0.01), " .. ", snappedf(hi,0.01), " minY=", snappedf(ylo,0.01))
		else:
			print(key, " none")
	print("RB_DONE")
	quit()
