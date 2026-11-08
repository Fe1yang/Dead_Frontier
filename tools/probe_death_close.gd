extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/death_%s.png" % n)
	print("SHOT ", n)
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("gate_timer", 1.0e9); main.set("obstacle_timer", 1.0e9)
	main.call("_spawn_zombie", -7.0, "walker")
	await create_timer(0.2).timeout
	var z = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q): z = q
	var cam = main.get("camera")
	cam.position = z.position + Vector3(1.6, 1.5, 3.0)
	cam.look_at(z.position + Vector3(0,1.1,0))
	await create_timer(0.2).timeout
	await _shot("0_alive")
	main.call("_hit_zombie", z, 1000000.0, "torso", z.global_position + Vector3(0,1.2,0))
	await create_timer(0.30).timeout
	await _shot("1_mid")
	await create_timer(0.45).timeout
	await _shot("2_down")
	print("DEATH_CLOSE_DONE")
	quit()
