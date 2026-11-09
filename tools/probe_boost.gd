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
	main.set("owned_vehicle", "GOLD_CAR"); main.set("vehicle_equipped", true); main.set("loadout_on", true)
	main.call("start_run", true, true)
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.call("set_weather", "clear")
	await create_timer(1.2).timeout
	var p = main.get("player")
	var fx = p.get("boost_fx")
	print("boost=", fx != null, " emitting=", fx.emitting if fx else false)
	main.call("debug_camera_at", Vector3(2.4, 1.9, 3.6), Vector3(0.0, 0.7, -1.0), 60.0)
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/boost.png")
	print("BOOST_DONE")
	quit()
