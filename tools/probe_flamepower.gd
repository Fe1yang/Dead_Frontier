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
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	for kind in ["walker", "brute"]:
		main.call("_spawn_zombie", -6.0, kind)
		await create_timer(0.3).timeout
		var z = null
		for q in (main.get("zombies") as Array):
			if String(q.get("kind")) == kind and not q.dead:
				z = q
		if z == null:
			print(kind, " not spawned")
			continue
		var t0 := Time.get_ticks_msec()
		var shots := 0
		while is_instance_valid(z) and not z.dead and shots < 60:
			p.call("fire")
			main.call("_fire")
			shots += 1
			await create_timer(0.12).timeout
		print(kind, " shots=", shots, " ms=", Time.get_ticks_msec() - t0, " dead=", (not is_instance_valid(z)) or z.dead)
	print("FP_DONE")
	quit()
