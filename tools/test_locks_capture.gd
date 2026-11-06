extends SceneTree
## Paid-survivor lock review: lobby cards, skin tab and the store's new sections,
## captured against the player's real (clean) save — Darius/Maya/tactical must be padlocked.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/locks"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.6).timeout
	game._clear_world(); game.enter_lobby()
	await create_timer(0.6).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/locks/lobby-chars.png")==OK)
	game.set_lobby_tab(2)
	await create_timer(0.4).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/locks/lobby-skins.png")==OK)
	game.set_lobby_tab(1)
	await create_timer(0.4).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/locks/lobby-pets.png")==OK)
	game._pointer_down(game.SIDE_STORE.get_center())
	await create_timer(0.5).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/locks/store-top.png")==OK)
	game.store_scroll=420.0
	await create_timer(0.3).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/locks/store-chars.png")==OK)
	print("LOCK_CAPTURE_PASS owned_chars=",game.owned_characters," owned_skins=",game.owned_skins," owned_pets=",game.owned_pets)
	game.queue_free(); await process_frame; quit()
