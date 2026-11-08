extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.8).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -7.0, "walker")
	await create_timer(0.25).timeout
	var z = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q): z = q
	var z0: float = z.position.z
	main.call("_hit_zombie", z, 1000000.0, "torso", z.global_position + Vector3(0,1.2,0))
	var samples := []
	for i in range(4):
		await create_timer(0.25).timeout
		samples.append(snappedf((z.position.z if is_instance_valid(z) else 99.0) - z0, 0.01))
	print("CORPSE dz per 0.25s = ", samples)
	print("bodies tracked = ", (main.get("dying_zombies") as Array).size())
	await create_timer(0.6).timeout
	print("after 1.6s valid=", is_instance_valid(z), " tracked=", (main.get("dying_zombies") as Array).size())
	print("CORPSE_DONE")
	quit()
