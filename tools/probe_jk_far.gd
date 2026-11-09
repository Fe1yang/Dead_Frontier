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
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.3).timeout
	main.call("_clear_world")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_zombie", -14.0, "jockey")
	await create_timer(0.4).timeout
	var jockey: Node3D = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q) and String(q.get("kind")) == "jockey":
			jockey = q
	if jockey == null:
		print("NO_JOCKEY"); quit(); return
	var cam := Camera3D.new(); cam.fov = 30.0
	main.add_child(cam); cam.make_current()
	for i in range(2):
		if not is_instance_valid(jockey): break
		var tp: Vector3 = jockey.position
		cam.position = Vector3(tp.x + 2.2, 1.3, tp.z + 6.5)
		cam.look_at(Vector3(tp.x, 0.8, tp.z))
		await create_timer(0.4).timeout
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/jk_far_%d.png" % i)
		print("FAR ", i)
	print("FAR_DONE")
	quit()
