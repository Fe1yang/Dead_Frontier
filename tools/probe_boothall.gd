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
	var n := 0
	for r in (main.get("roads") as Array):
		for c in r.get_children():
			if not String(c.name).begins_with("phone_booth"): continue
			n += 1
			print("  ", c.name, " x=", snappedf(c.global_position.x,0.01), " z=", snappedf(c.global_position.z,0.01), " rot=", snappedf(c.rotation.y,0.01))
	print("total booths=", n)
	print("BA_DONE")
	quit()
