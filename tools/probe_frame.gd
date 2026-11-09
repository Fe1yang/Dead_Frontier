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
	var frames: Array[float] = []
	var last := Time.get_ticks_usec()
	var t0 := last
	while Time.get_ticks_usec() - t0 < 25000000:
		await process_frame
		var now := Time.get_ticks_usec()
		frames.append((now - last) / 1000.0)
		last = now
	frames.sort()
	var n := frames.size()
	var over33 := 0
	var over50 := 0
	for f in frames:
		if f > 33.0: over33 += 1
		if f > 50.0: over50 += 1
	print("frames=%d  p50=%.1fms  p95=%.1fms  p99=%.1fms  max=%.1fms  >33ms=%d  >50ms=%d" % [
		n, frames[int(n*0.5)], frames[int(n*0.95)], frames[int(n*0.99)], frames[n-1], over33, over50])
	print("FR_DONE")
	quit()
