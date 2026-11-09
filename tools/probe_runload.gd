extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var t0 := Time.get_ticks_msec()
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	# the real path: the loading screen, not start_run() directly
	var worst_load := 0.0
	var prev := Time.get_ticks_usec()
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
		var now := Time.get_ticks_usec()
		var ms := float(now - prev) / 1000.0
		prev = now
		if ms > worst_load: worst_load = ms
	var worst_play := 0.0
	for i in range(60):
		await process_frame
		var now2 := Time.get_ticks_usec()
		var ms2 := float(now2 - prev) / 1000.0
		prev = now2
		if ms2 > worst_play: worst_play = ms2
	print("RUNLOAD worst_loading_ms=", snappedf(worst_load,0.1),
		" worst_first_playing_ms=", snappedf(worst_play,0.1),
		" loading_frames=", frames,
		" roads=", (main.get("roads") as Array).size(),
		" state=", main.get("state"))
	print("RL_DONE")
	quit()
