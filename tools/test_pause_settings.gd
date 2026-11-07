extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.5).timeout
	game.start_run()
	await create_timer(1.2).timeout
	game.state="paused"
	await create_timer(0.3).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/pause_settings.png")==OK)
	# tap the settings button
	game._pointer_down(Rect2(66,468,408,58).get_center())
	assert(game.state=="settings" and game.settings_return_state=="paused")
	await create_timer(0.3).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/pause_settings_page.png")==OK)
	# back returns to the pause menu
	game._pointer_down(Rect2(66,810,408,64).get_center())
	assert(game.state=="paused")
	print("PAUSE_SETTINGS_PASS")
	game.queue_free(); await process_frame; quit()
