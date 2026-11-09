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
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("set_weather", "clear")
	main.call("_spawn_pothole")
	await create_timer(0.8).timeout
	var cones := 0
	for o in (main.get("obstacles") as Array):
		if String(o.get("kind")) == "cone":
			cones += 1
	print("cones spawned=", cones)
	main.call("debug_camera_at", Vector3(2.2, 1.6, 3.0), Vector3(0.0, 0.2, -6.0), 60.0)
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/cones.png")
	print("CONES_DONE")
	quit()
