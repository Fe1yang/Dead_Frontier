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
	await create_timer(0.5).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.call("set_weather", "clear")
	await create_timer(2.0).timeout
	main.call("debug_camera_at", Vector3(0.0, 2.2, 3.4), Vector3(0.0, 0.0, -6.0), 60.0)
	await create_timer(0.6).timeout
	var path = OS.get_environment("SHOT_OUT")
	if path == "":
		path = "res://tools/ground.png"
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png(path)
	print("GROUND_DONE ", path)
	quit()
