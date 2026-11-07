extends SceneTree
## In-run pose review: Riley and Yuhang mid-run, front three-quarter view.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/pose"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.6).timeout
	for ch in [1,4]:
		game._clear_world(); game.enter_lobby()
		await create_timer(0.3).timeout
		game.owned_characters[4]=true
		game.select_character(ch)
		game.start_run(); game.state="playing"; game.shot_timer=999; game.hint_time=0
		game.touch_controls=false
		await create_timer(1.2).timeout; await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png("res://diagnostics/pose/run-char%d-a.png"%ch)==OK)
		await create_timer(0.5).timeout; await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png("res://diagnostics/pose/run-char%d-b.png"%ch)==OK)
	print("RUN_POSE_PASS")
	game.queue_free(); await process_frame; quit()
