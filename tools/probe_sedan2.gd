extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/car_%s.png" % n)
	print("SHOT ", n)
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.5).timeout
	main.call("set_lobby_tab", 3)
	await create_timer(0.6).timeout
	main.set("lobby_scroll", main.call("lobby_max_scroll"))
	await create_timer(0.5).timeout
	await _shot("1_cards_end")
	# select the car card (index 5) and look at the stage
	main.call("_lobby_tap", (main.call("lobby_card_rect", 5) as Rect2).get_center())
	await create_timer(0.9).timeout
	print("CHOICE=", main.get("vehicle_choice"), " bike_index=", main.get("lobby").get("bike_index"))
	await _shot("2_stage")
	print("DONE")
	quit()
