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
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_chase_begin")
	await create_timer(0.8).timeout
	var ch = main.get("chaser")
	var cam := Camera3D.new(); cam.fov=48.0
	main.add_child(cam); cam.make_current()
	if ch != null:
		cam.position = ch.position + Vector3(1.6, 2.2, 4.6)
		cam.look_at(ch.position + Vector3(0, 2.0, 0))
	await create_timer(0.5).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pursuer_chase_shot.png")
	print("CHASE_SHOT_DONE")
	quit()
