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
	main.call("_spawn_zombie", -12.0, "jockey")
	await create_timer(0.2).timeout
	main.call("debug_camera_at", Vector3(0.0, 1.5, 3.2), Vector3(0.0, 0.9, -8.0), 60.0)
	for i in range(4):
		await create_timer(0.45).timeout
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/jkrun_%d.png" % i)
	var z = null
	for q in (main.get("zombies") as Array):
		if String(q.get("kind")) == "jockey":
			z = q
	if z: print("JOCKEY_END ", z.position)
	print("JKRUN_DONE")
	quit()
