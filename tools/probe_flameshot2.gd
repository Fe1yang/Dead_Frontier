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
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	await create_timer(0.4).timeout
	# let the jet run for a moment, then shoot from the side so the cone is visible
	for i in range(10):
		p.call("pulse_flame")
		main.call("_fire")
		await create_timer(0.05).timeout
	var c: Vector3 = p.position + Vector3(2.6, 1.5, 1.6)
	main.call("debug_camera_at", c, p.position + Vector3(0, 0.9, -4.5), 60.0)
	await create_timer(0.12).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/flame_new.png")
	print("FLAME2_DONE")
	quit()
