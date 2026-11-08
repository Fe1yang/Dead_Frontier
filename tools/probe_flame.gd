extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	main.call("_spawn_zombie", -3.5, "walker")
	await create_timer(0.5).timeout
	var z = (main.get("zombies") as Array).back()
	print("BEFORE health=", snappedf(z.health, 0.1), " burning=", z.burn_timer > 0.0)
	p.call("fire")
	main.call("_fire")
	await create_timer(0.5).timeout
	print("AFTER 0.5s health=", snappedf(z.health, 0.1), " burning=", snappedf(z.burn_timer,0.1))
	await create_timer(0.8).timeout
	print("AFTER 1.3s health=", snappedf(z.health, 0.1), " burning=", snappedf(z.burn_timer,0.1))
	print("FLAME_DONE")
	quit()
