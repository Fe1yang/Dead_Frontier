extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.call("set_lobby_tab", 3)
	await create_timer(0.5).timeout
	# tap the tank card (index 4)
	var r: Rect2 = main.call("lobby_card_rect", 4)
	main.call("_lobby_tap", r.get_center())
	await create_timer(0.35).timeout
	print("TOAST text=", main.get("store_toast_text"), " t=", snappedf(float(main.get("store_toast")),0.01))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/veh_toast.png")
	print("VEHTOAST_DONE")
	quit()
