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
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	var t0 := Time.get_ticks_usec()
	var last := t0
	var frames := 0
	var spikes := 0
	var lines := 0
	while Time.get_ticks_usec() - t0 < 22000000:
		await process_frame
		var now := Time.get_ticks_usec()
		var ms := (now - last) / 1000.0
		last = now
		frames += 1
		if ms > 33.0:
			spikes += 1
			if lines < 10:
				lines += 1
				var proc_ms := Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0
				var phys_ms := Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0
				var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
				var objs := Performance.get_monitor(Performance.OBJECT_COUNT)
				var nodes := Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
				print("SPIKE frame=%d total=%.0fms process=%.1fms physics=%.1fms draws=%.0f nodes=%.0f objs=%.0f" % [
					frames, ms, proc_ms, phys_ms, draws, nodes, objs])
	print("SUMMARY frames=%d spikes=%d" % [frames, spikes])
	print("PF_DONE")
	quit()
