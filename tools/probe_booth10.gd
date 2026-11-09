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
	await create_timer(1.0).timeout
	var target: Vector3 = Vector3.ZERO
	var found := false
	for r in (main.get("roads") as Array):
		for c in r.get_children():
			if String(c.name).begins_with("phone_booth"):
				target = c.global_position
				found = true
				break
		if found: break
	print("TARGET ", target)
	if not found:
		quit()
		return
	# stand on the road looking at the booth, from 6 m away and 2 m to its left
	main.call("debug_camera_at", Vector3(target.x - 4.5, target.y + 1.6, target.z + 5.0), Vector3(target.x, target.y + 1.3, target.z), 50.0)
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/booth.png")
	print("SHOT_DONE")
	quit()
