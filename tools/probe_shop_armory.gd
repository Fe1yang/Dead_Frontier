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
	await create_timer(0.5).timeout
	main.call("open_shop")
	await create_timer(1.0).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/shop_with_armory.png")
	# tap the armory button
	main.call("_pointer_down", Vector2(460, 100))
	await create_timer(0.8).timeout
	print("STATE_AFTER_TAP=", main.get("state"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/armory_open.png")
	print("SHOPARM_DONE")
	quit()
