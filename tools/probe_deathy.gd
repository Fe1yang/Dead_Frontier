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
	await create_timer(0.6).timeout
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -5.0, "walker")
	await create_timer(0.4).timeout
	var z = (main.get("zombies") as Array).back()
	z.call("take_hit", 9999.0)
	z.call("die")
	var low := 0.0
	for i in range(30):
		await create_timer(0.05).timeout
		if is_instance_valid(z):
			var l: float = z.call("_body_low_y")
			low = minf(low, l)
	print("lowest body y during the fall = ", snappedf(low, 0.01))
	print("ZDT_DONE")
	quit()
