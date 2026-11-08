extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/zanim_%s.png" % n)
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
	main.set("spawn_timer", 1.0e9)
	# a row of walkers/runner so their walk clips can be compared
	var xs := [-2.4, -1.2, 0.0, 1.2, 2.4]
	for i in range(5):
		main.call("_spawn_zombie", -8.0 - float(i), "walker" if i < 4 else "runner")
	await create_timer(0.5).timeout
	for z in (main.get("zombies") as Array):
		if is_instance_valid(z):
			var ap = z.get("animation_player")
			if ap: print("ZOMBIE kind=", z.get("kind"), " clip=", ap.current_animation, " speed=", ap.speed_scale)
	await _shot("1_walks")
	# kill the nearest one and watch it fall
	var target = null
	for z in (main.get("zombies") as Array):
		if is_instance_valid(z) and not z.get("dead"):
			target = z
			break
	if target != null:
		main.call("_hit_zombie", target, 1000000.0, "torso", target.global_position + Vector3(0,1.2,0))
		print("KILLED clip=", target.get("animation_player").current_animation, " dead=", target.get("dead"))
	await create_timer(0.45).timeout
	await _shot("2_falling")
	await create_timer(1.2).timeout
	await _shot("3_after")
	print("ZANIM_DONE")
	quit()
