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
	main.set("spawn_timer", 1.0e9)
	main.call("set_weather", "clear")
	main.call("_spawn_zombie", -4.5, "jockey")
	main.call("_spawn_zombie", -7.0, "walker")
	await create_timer(1.2).timeout
	main.call("debug_camera_at", Vector3(1.6, 1.5, 1.2), Vector3(0.0, 0.75, -5.0), 62.0)
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/jockey.png")
	print("JKS_DONE")
	quit()
