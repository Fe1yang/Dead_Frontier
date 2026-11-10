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
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	var last := Time.get_ticks_usec()
	var t0 := last
	var reported := 0
	while Time.get_ticks_usec() - t0 < 30000000:
		await process_frame
		var now := Time.get_ticks_usec()
		var ms := (now - last) / 1000.0
		last = now
		if ms > 80.0 and reported < 8:
			reported += 1
			print("SPIKE %.0f ms  dist=%.0f  zombies=%d  roads=%d  pickups=%d  effects=%d  crates=%d  barrels=%d  blood=%d" % [
				ms, float(main.get("distance")),
				(main.get("zombies") as Array).size(), (main.get("roads") as Array).size(),
				(main.get("pickups") as Array).size(), (main.get("effects") as Array).size(),
				(main.get("crates") as Array).size(), (main.get("barrels") as Array).size(),
				(main.get("blood_pools") as Array).size()])
	print("SP_DONE")
	quit()
