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
	main.call("_spawn_zombie", -6.0, "jockey")
	await create_timer(0.35).timeout
	var z = null
	for q in (main.get("zombies") as Array):
		if String(q.get("kind")) == "jockey":
			z = q
	if z == null:
		print("NO_JOCKEY")
		quit()
		return
	var at: Vector3 = z.position
	print("JOCKEY_AT ", at)
	main.call("debug_camera_at", at + Vector3(1.5, 1.0, 2.0), at + Vector3(0, 0.6, 0), 52.0)
	await create_timer(0.25).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/jockey_only.png")
	print("JKO_DONE")
	quit()
