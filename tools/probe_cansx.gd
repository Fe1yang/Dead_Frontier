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
	var bad := 0
	var total := 0
	for r in (main.get("roads") as Array):
		for c in r.get_children():
			var nm := String(c.name)
			if not (nm.begins_with("can_a") or nm.begins_with("can_b") or nm.begins_with("can_c") or nm.begins_with("can_d")):
				continue
			total += 1
			var ax: float = absf(c.global_position.x)
			if ax < 8.9 or ax > 12.2:
				bad += 1
	print("cans=", total, " outside 9..12: ", bad)
	print("CX_DONE")
	quit()
