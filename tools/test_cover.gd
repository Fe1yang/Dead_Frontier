extends SceneTree
## Launch screen check: the restored cover poster, then the main menu after one tap.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/cover"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.4).timeout
	print("STATE_AT_LAUNCH ",game.state)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/cover/cover.png")==OK)
	game._pointer_down(Vector2(270,480))
	await create_timer(0.2).timeout
	print("STATE_AFTER_TAP ",game.state)
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/cover/after-tap.png")==OK)
	print("COVER_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
