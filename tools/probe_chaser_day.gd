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
	main.call("start_run", false, true)
	await create_timer(1.6).timeout
	main.call("set_weather", "clear")
	var ch = main.get("chaser")
	if ch == null:
		print("NO_CHASER")
		quit()
		return
	var pos: Vector3 = ch.global_position
	print("CHASER at ", pos)
	# stand in front of it (the pursuer trails the player at +Z) and look at the chest
	main.call("debug_camera_at", Vector3(pos.x + 1.8, 2.6, pos.z - 4.6), Vector3(pos.x, 1.9, pos.z), 55.0)
	await create_timer(0.7).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/chaser_day.png")
	print("CH_DAY_DONE")
	quit()
