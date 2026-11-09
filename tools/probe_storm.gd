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
	await create_timer(0.2).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("set_weather", "storm")
	main.set("lightning_timer", 0.15)     # force a strike almost immediately
	await create_timer(0.5).timeout
	var shot := 0
	for i in range(90):
		var t := float(main.get("lightning_t"))
		if t >= 0.03 and t <= 0.10 and shot == 0:
			await RenderingServer.frame_post_draw
			root.get_viewport().get_texture().get_image().save_png("res://tools/storm_flash.png")
			print("FLASH at lightning_t=", snappedf(t, 0.01), " thunder_delay=", snappedf(float(main.get("thunder_delay")), 0.02))
			shot = 1
		await process_frame
		if shot == 1 and t < 0.0:
			break
	print("STORM_DONE shot=", shot)
	quit()
