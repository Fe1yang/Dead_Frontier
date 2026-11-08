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
	await create_timer(0.6).timeout
	main.call("set_lobby_tab", 0)
	main.call("_lobby_tap", (main.call("lobby_card_rect", 4) as Rect2).get_center())
	await create_timer(2.0).timeout
	var ls = main.get("lobby")
	var ap = ls.get("actor_anim")
	print("J clip=", ap.current_animation if ap else "none", " t=", snappedf(ap.current_animation_position,0.1) if ap else -1)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/jian_fold.png")
	print("JF_DONE")
	quit()
