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
	var counts := {}
	for r in (main.get("roads") as Array):
		for c in r.get_children():
			var nm := String(c.name)
			for k in ["phone_booth", "bench", "trash_bin", "trash_can", "manhole", "hydrant", "can_a", "can_b", "can_c", "can_d"]:
				if nm.begins_with(k):
					counts[k] = int(counts.get(k, 0)) + 1
					break
	var keys := counts.keys()
	keys.sort()
	for k in keys:
		print("  ", k, " = ", counts[k])
	print("total props=", counts.values().reduce(func(a,b): return a+b, 0))
	print("PX11_DONE")
	quit()
