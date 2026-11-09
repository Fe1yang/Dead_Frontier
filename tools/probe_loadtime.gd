extends SceneTree
var main: Node
var t0 := 0
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	t0 = Time.get_ticks_msec()
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	print("lobby up at ", Time.get_ticks_msec() - t0, " ms")
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	var t1 := Time.get_ticks_msec()
	main.call("_begin_loading", "run")
	var worst := 0
	var last := Time.get_ticks_msec()
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 900:
		await process_frame
		var now := Time.get_ticks_msec()
		worst = maxi(worst, now - last)
		last = now
		frames += 1
	print("loading took ", Time.get_ticks_msec() - t1, " ms, worst frame ", worst, " ms, districts=", (main.get("roads") as Array).size())
	# first seconds of play: worst frame
	worst = 0
	last = Time.get_ticks_msec()
	var start := last
	while Time.get_ticks_msec() - start < 4000:
		await process_frame
		var now2 := Time.get_ticks_msec()
		worst = maxi(worst, now2 - last)
		last = now2
	print("first 4 s of play: worst frame ", worst, " ms")
	print("LT_DONE")
	quit()
