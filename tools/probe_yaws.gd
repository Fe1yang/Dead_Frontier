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
	p.call("set_weapon", "RIFLE")
	await create_timer(0.4).timeout
	var degs := [0, 90, 180, 270]
	for d in degs:
		var wm = p.get("weapon_model")
		# keep the base orientation from the normaliser, replace only its yaw
		wm.rotation.y = deg_to_rad(float(d))
		await create_timer(0.2).timeout
		paused = true
		cam.global_position = p.global_position + Vector3(1.35, 1.85, 1.6)
		cam.look_at(p.global_position + Vector3(0, 1.32, -0.15), Vector3.UP)
		cam.fov = 40.0
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/yaw_%d.png" % d)
		paused = false
	print("YAWS_DONE")
	quit()
