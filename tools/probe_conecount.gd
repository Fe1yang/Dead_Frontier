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
	var peak := 0
	for i in range(900):
		main.call("_tick_obstacles", 0.016)
		peak = maxi(peak, int(main.call("_cone_obstacle_count")))
		if i % 120 == 0:
			main.call("_spawn_obstacle_pattern")
	print("PEAK_CONES ", peak)
	print("CONEPROBE_DONE")
	quit()
