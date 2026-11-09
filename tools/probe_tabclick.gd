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
	var r: Rect2 = main.call("lobby_tab_rect", 4)
	print("tab4 rect=", r)
	main.call("_lobby_tap", r.get_center())
	await create_timer(0.6).timeout
	print("tab after click=", main.get("lobby_tab"), " count=", main.call("lobby_item_count"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/tab4.png")
	print("TAB4_DONE")
	quit()
