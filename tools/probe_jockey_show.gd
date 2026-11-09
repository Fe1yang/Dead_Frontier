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
	await create_timer(0.2).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_zombie", -4.5, "jockey")
	await create_timer(0.35).timeout
	var jockey: Node3D = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q) and String(q.get("kind")) == "jockey":
			jockey = q
	if jockey == null:
		print("NO_JOCKEY"); quit(); return
	for i in range(4):
		if not is_instance_valid(jockey):
			print("JOCKEY_GONE at shot ", i); break
		var cam: Camera3D = main.get("camera")
		cam.position = jockey.position + Vector3(1.1, 1.0, 2.4)
		cam.look_at(jockey.position + Vector3(0, 0.5, 0))
		await create_timer(0.45).timeout
		if not is_instance_valid(jockey): continue
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/jockey_show_%d.png" % i)
		print("SHOT ", i, " z=", snappedf(jockey.position.z, 0.1))
	print("SHOW_DONE")
	quit()
