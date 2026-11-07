extends SceneTree
## Jian review: base model and the scout outfit on the platform, plus the store row.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/jian"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.6).timeout
	game._clear_world(); game.enter_lobby()
	await create_timer(0.5).timeout
	game.owned_characters[4]=true
	game.select_character(4)
	await create_timer(0.8).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/jian/lobby-jian.png")==OK)
	game.owned_skins[3]=true
	game.select_skin(3)
	await create_timer(0.8).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/jian/lobby-jian-scout.png")==OK)
	game._pointer_down(game.SIDE_STORE.get_center())
	await create_timer(0.5).timeout
	game.store_scroll=420.0
	await create_timer(0.3).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/jian/store-chars.png")==OK)
	print("JIAN_LOBBY_PASS")
	game.queue_free(); await process_frame; quit()
