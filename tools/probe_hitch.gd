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
	var p = main.get("player")
	var t0 := Time.get_ticks_usec()
	for i in range(600):
		# drive forward and wiggle the stick like a thumb would
		p.set("target_x", sin(float(i) * 0.2) * 1.6)
		p.set("left_stick", Vector2(sin(float(i)*0.1), -1.0))
		if is_instance_valid(main.get("camera")):
			pass
		await process_frame
	var ms := float(Time.get_ticks_usec() - t0) / 1000.0
	print("SIM 600 frames in ", snappedf(ms, 1.0), " ms")
	print("HITCHPROBE_DONE")
	quit()
