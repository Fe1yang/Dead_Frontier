extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	var main := current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	# let the warm-up queue run (it ticks while state != playing)
	await create_timer(2.0).timeout
	var zombies := 0
	var pickups := 0
	for n in main.get_children():
		var s = n.get_script()
		if s != null and String(s.resource_path).ends_with("zombie_3d.gd"): zombies += 1
		if s != null and String(s.resource_path).ends_with("pickup_3d.gd"): pickups += 1
	print("LEAK warmup zombies in main scene=", zombies, " pickups=", pickups)
	quit()
