extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var game := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(game)
	await process_frame
	game.open_store()
	for item in game.store_layout():
		if item.get("id","")=="coins_3":
			game.store_scroll=clampf((item.rect as Rect2).position.y-250.0,0.0,game.store_max_scroll())
	await create_timer(0.25).timeout
	await RenderingServer.frame_post_draw
	var path := "C:/Users/user/Documents/kimi/tasks/2026-11-04/00-09-49-288c0219/diagnostics/coin_bag/in-game.png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("CAPTURE_COIN_BAG_SAVED ",path)
	quit()
