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
	# wait for the loading screen to finish warming
	for i in range(300):
		if String(main.get("state")) != "loading": break
		await process_frame
	await create_timer(0.6).timeout
	print("state=", main.get("state"), " warmup_done=", main.get("warmup_done"), " queue=", (main.get("warmup_queue") as Array).size())
	print("zombies=", (main.get("zombies") as Array).size())
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/first_run.png")
	print("FIRSTRUN_DONE")
	quit()
