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
	main.set("spawn_timer", 1.0e9)
	main.call("set_weather", "clear")
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	main.call("_spawn_zombie", -7.0, "walker")
	await create_timer(0.5).timeout
	# camera sits behind-right of the survivor, looking down the barrel line
	main.call("debug_camera_at", Vector3(1.4, 1.65, 3.0), Vector3(0.0, 0.85, -5.0), 62.0)
	for i in range(8):
		p.call("pulse_flame")
		main.call("_fire")
		await create_timer(0.05).timeout
	await create_timer(0.10).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/flame_jet.png")
	print("FLAMEJET_DONE")
	quit()
