extends SceneTree
## Screenshot the store scrolled to the 载具 section into tools/store_vehicles.png.

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
	main.call("open_store")
	await create_timer(0.3).timeout
	# scroll so the vehicle section sits just under the header
	var layout: Array = main.call("store_layout")
	for it in layout:
		if it.has("header") and String(it.header) == "vehicle":
			var r: Rect2 = it.rect
			main.set("store_scroll", maxf(0.0, r.position.y - 150.0))
			break
	await create_timer(1.2).timeout
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://tools/store_vehicles.png")
	print("CAPTURE_OK ", img.get_width(), "x", img.get_height(), " scroll=", main.get("store_scroll"))
	quit()
