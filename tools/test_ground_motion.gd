extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/ground-motion"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.set_process(false); game.state="playing"; game.set_weather("clear"); game.distance=0; game._apply_day_night()
	game.camera.position=Vector3(0,6.4,13.5); game.camera.fov=52; game.camera.h_offset=0; game.camera.v_offset=0
	game.camera.look_at(Vector3(0,1,-8))
	for step in range(8):
		for road in game.roads: road.position.z+=2.0
		game.distance=step*20.0
		await create_timer(0.12).timeout; await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png("res://diagnostics/ground-motion/frame-%02d.png"%step)==OK)
	print("GROUND_MOTION_TEST_PASS captured 8 positions across live city intersections")
	quit()
