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
	var worst := 0.0
	var prev := Time.get_ticks_usec()
	main.set("stamina", load("res://scripts/stamina.gd").new() if false else main.get("stamina"))
	main.call("start_run", true, true)
	for i in range(120):
		await process_frame
		var now := Time.get_ticks_usec()
		var ms := float(now - prev) / 1000.0
		prev = now
		if ms > worst: worst = ms
	print("RUNSTART worst_frame_ms=", snappedf(worst,0.1), " state=", main.get("state"))
	print("RS_DONE")
	quit()
