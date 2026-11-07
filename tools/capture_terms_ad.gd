extends SceneTree
## Review shots: first-launch terms gate + the health-ad prompt.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/hud"))
	var game: Node3D = (load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.8).timeout
	# Terms gate: force the first-launch state and scroll a little to prove scrolling works.
	game.terms_accepted = false
	game.terms_scroll = game.hud.terms_max_scroll() * 0.5
	game.state = "terms"
	await create_timer(0.6).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/hud/terms.png") == OK)
	# Health ad prompt: mid-run at half health, tap the red cross.
	game.terms_accepted = true
	game.start_run()
	game.player.health = game.player.max_health * 0.5
	await create_timer(1.4).timeout
	if game.state == "intro": game._finish_intro()
	await create_timer(0.8).timeout
	game._pointer_down(game.health_plus_rect.get_center())
	await create_timer(0.6).timeout; await RenderingServer.frame_post_draw
	assert(game.state == "health_ad")
	assert(root.get_texture().get_image().save_png("res://diagnostics/hud/health_ad.png") == OK)
	print("TERMS_AD_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
