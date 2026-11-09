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
	main.call("set_weather", "clear")
	var p = main.get("player")
	print("molotovs before=", p.get("molotov_count"))
	main.call("_spawn_zombie", -5.0, "walker")
	await create_timer(0.4).timeout
	var z = (main.get("zombies") as Array).back()
	var hp0: float = z.health
	main.call("_throw_ordnance", "molotov")
	await create_timer(2.2).timeout
	print("molotovs after=", p.get("molotov_count"), " zombie burning=", z.burn_timer if is_instance_valid(z) else -1.0, " hp ", hp0, " -> ", z.health if is_instance_valid(z) else -1.0)
	print("MO_DONE")
	quit()
