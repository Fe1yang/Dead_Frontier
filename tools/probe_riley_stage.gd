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
	main.call("set_lobby_tab", 0)
	main.call("_lobby_tap", (main.call("lobby_card_rect", 1) as Rect2).get_center())
	await create_timer(1.1).timeout
	var a = main.get("lobby").get("actor")
	print("actor visible=", a.visible if a != null and is_instance_valid(a) else "none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/riley_stage3.png")
	print("STAGE_DONE")
	quit()
