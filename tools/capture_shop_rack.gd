extends SceneTree
## Screenshot the supply-truck weapon rack so the pistol orientation can be checked.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	var main := current_scene
	if main == null:
		quit(1)
		return
	await create_timer(1.2).timeout
	paused = false
	for _i in range(8):
		if String(main.get("state")) == "character_select":
			break
		main.enter_lobby()
		await create_timer(0.4).timeout
	main.call("open_shop")
	await create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://tools/shop_rack.png")
	print("CAPTURE_OK ", img.get_width(), "x", img.get_height(), " state=", main.get("state"))
	quit()
