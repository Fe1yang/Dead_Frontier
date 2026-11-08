extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.set("character_choice", 4)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -9.0, "walker")
	await create_timer(0.5).timeout
	var p = main.get("player")
	var base: Vector3 = p.global_position
	main.call("debug_camera_at", base + Vector3(1.1, 1.55, 1.9), base + Vector3(0, 1.25, 0), 40.0)
	await create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/jian_look.png")
	print("LOOK_DONE")
	quit()
