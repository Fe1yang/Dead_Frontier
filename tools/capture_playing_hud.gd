extends SceneTree
## One-frame capture of the live-run HUD: hearts, cross, banner — to review the health plus.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/hud"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.8).timeout
	game.stamina.value=game.stamina.CAP
	game.start_run()
	game.player.health=game.player.max_health*0.5
	await create_timer(1.2).timeout
	if game.state=="intro": game._finish_intro()
	await create_timer(1.0).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/hud/playing.png")==OK)
	print("HUD_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
