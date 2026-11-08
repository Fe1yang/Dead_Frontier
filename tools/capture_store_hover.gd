extends SceneTree
## Screenshot the store with the pointer parked on the gold bike row (hover tooltip).

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
	var layout: Array = main.call("store_layout")
	var target := Vector2(270, 600)
	for it in layout:
		if it.has("header") and String(it.header) == "vehicle":
			main.set("store_scroll", maxf(0.0, (it.rect as Rect2).position.y - 150.0))
			break
	await create_timer(1.0).timeout
	for it in main.call("store_layout"):
		if it.has("pack") and String(it.pack.get("id", "")).begins_with("char_"):
			var r: Rect2 = main.call("store_screen_rect", it)
			target = r.get_center()
			break
	var ev := InputEventMouseMotion.new()
	ev.position = target
	ev.global_position = target
	main.get_viewport().push_input(ev)
	await create_timer(0.4).timeout
	var hud: Node = main.get("hud")
	print("MOUSE input=", root.get_mouse_position(), " local=", hud.get_local_mouse_position() if hud else "nohud")
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://tools/store_hover_char.png")
	print("CAPTURE_OK ", img.get_width(), "x", img.get_height(), " target=", target)
	quit()
