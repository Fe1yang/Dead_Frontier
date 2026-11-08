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
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	var cam: Camera3D = null
	for c in main.find_children("*", "Camera3D", true, false):
		cam = c; break
	for w in ["PISTOL", "SHOTGUN", "RIFLE", "SNIPER", "LAUNCHER"]:
		p.call("set_weapon", w)
		await create_timer(0.4).timeout
		if cam and is_instance_valid(p):
			cam.global_position = p.global_position + Vector3(0.9, 1.45, 0.85)
			cam.look_at(p.global_position + Vector3(0, 1.30, 0), Vector3.UP)
			cam.fov = 38.0
		await create_timer(0.15).timeout
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/close_%s.png" % w)
	print("CLOSE_DONE")
	quit()
