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
	main.call("_spawn_zombie", -6.0, "walker")
	await create_timer(0.25).timeout
	var z = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q): z = q
	main.call("_hit_zombie", z, 1000000.0, "torso", z.global_position + Vector3(0,1.2,0))
	await create_timer(0.05).timeout
	print("ROAD zombie valid after kill=", is_instance_valid(z), " corpses=", (main.get("dying_zombies") as Array).size())
	var w = null
	for q in (main.get("watchers") as Array):
		if is_instance_valid(q) and not q.get("dead"): w = q; break
	if w != null:
		main.call("_hit_zombie", w, 1000000.0, "head", w.global_position + Vector3(0,1.6,0))
		await create_timer(0.2).timeout
		print("WATCHER valid=", is_instance_valid(w), " clip=", (w.get("animation_player") as AnimationPlayer).current_animation if is_instance_valid(w) else "-")
	else:
		print("WATCHER none in scene")
	print("BLAST_DONE")
	quit()
