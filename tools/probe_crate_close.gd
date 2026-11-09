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
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.call("set_weather", "clear")
	await create_timer(0.4).timeout
	main.call("_spawn_crates")
	await create_timer(0.5).timeout
	# bring the pair of platforms within arm's reach so the shape is readable
	var crates: Array = main.get("crates")
	for c in crates:
		if is_instance_valid(c):
			c.position.z = -7.0
	await create_timer(0.5).timeout
	main.call("debug_camera_at", Vector3(0.0, 2.0, 2.6), Vector3(0.0, 0.55, -7.0), 62.0)
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/crate_close.png")
	print("CRATE_CLOSE_DONE")
	quit()
