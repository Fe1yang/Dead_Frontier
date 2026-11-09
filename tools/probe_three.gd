extends SceneTree
var main: Node
var cam: Camera3D
func _initialize() -> void:
	call_deferred("_run")
func _shoot(kind: String, tag: String) -> void:
	main.call("_clear_world")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_zombie", -9.0, kind)
	await create_timer(0.35).timeout
	var target: Node3D = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q) and String(q.get("kind")) == kind:
			target = q
	if target == null:
		print("MISS ", kind); return
	print("SPAWNED ", kind, " pos=", target.position)
	for i in range(3):
		if not is_instance_valid(target): break
		var tp: Vector3 = target.position
		# stand in front of it (it walks toward +Z) and look back at it
		cam.position = Vector3(tp.x + 1.1, 1.05, tp.z + 3.0)
		cam.look_at(Vector3(tp.x, 0.75, tp.z))
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/%s_%d.png" % [tag, i])
		print("SHOT ", tag, i, " z=", snappedf(target.position.z, 0.1))
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
	cam = Camera3D.new(); cam.fov = 50.0
	main.add_child(cam); cam.make_current()
	await _shoot("bomber", "bm_male")
	await _shoot("bomber_female", "bm_female")
	await _shoot("jockey", "jk_walk")
	print("THREE_DONE")
	quit()
