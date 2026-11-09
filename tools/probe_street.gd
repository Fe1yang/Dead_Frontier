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
	await create_timer(2.0).timeout
	var props := 0
	for road in (main.get("roads") as Array):
		props += road.find_children("*", "MeshInstance3D", true, false).size()
	print("road meshes now=", props)
	main.call("debug_camera_at", Vector3(3.0, 2.0, 6.0), Vector3(-1.0, 0.6, -10.0), 55.0)
	await create_timer(0.5).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/street.png")
	print("ST_DONE")
	quit()
