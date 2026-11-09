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
	await create_timer(0.5).timeout
	var roads = main.get("roads") as Array
	var vis := 0
	var zs := []
	for r in roads:
		if r.visible: vis += 1
		if zs.size() < 30: zs.append(snappedf(r.position.z, 1.0))
	print("roads=", roads.size(), " visible=", vis)
	print("z=", zs)
	print("RV_DONE")
	quit()
