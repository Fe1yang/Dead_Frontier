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
	var worst := 0
	var prev := Time.get_ticks_usec()
	var frames := 0
	while Time.get_ticks_msec() - t0 < 30000:
		await process_frame
		var now := Time.get_ticks_usec()
		var ms := float(now - prev) / 1000.0
		prev = now
		frames += 1
		if ms > worst: worst = ms
		if String(main.get("state")) == "character_select" or String(main.get("state")) == "cover":
			if frames > 60: break
	print("BOOT ms_to_lobby=", Time.get_ticks_msec() - t0, " frames=", frames, " worst_frame_ms=", snappedf(worst,0.1), " state=", main.get("state"))
	print("BOOT_DONE")
	quit()
