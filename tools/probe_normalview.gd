extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	await create_timer(2.0).timeout
	main.call("set_weather", "clear")
	await create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/normal_view.png")
	var vis := 0
	for r in (main.get("roads") as Array):
		if r.visible: vis += 1
	print("NORMAL_VIEW roads_visible=", vis)
	print("NV_DONE")
	quit()
