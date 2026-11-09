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
	var count := 0
	for r in (main.get("roads") as Array):
		for n in r.get_children():
			var nm := String(n.name)
			if nm.begins_with("lamp_modern") or nm.begins_with("lamp_round"):
				count += 1
				if count <= 6:
					print("  ", nm, " world=", n.global_position)
	print("lamps total=", count)
	print("LX_DONE")
	quit()
