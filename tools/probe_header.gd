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
	await create_timer(0.3).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.4).timeout
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	# a readable horde in front of the survivor
	for i in range(7):
		main.call("_spawn_zombie", -6.0 - float(i) * 2.2, "walker")
	await create_timer(1.0).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/header_shot.png")
	print("HEADER_SHOT_DONE")
	quit()
