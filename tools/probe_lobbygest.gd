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
	var ls = main.get("lobby")
	for idx in [1, 0]:
		main.call("_lobby_tap", (main.call("lobby_card_rect", idx) as Rect2).get_center())
		await create_timer(1.0).timeout
		var ap = ls.get("actor_anim")
		print("CHAR ", idx, " idle=", ls.get("idle_clip_name"), " playing=", ap.current_animation if ap else "none", " len=", snappedf(ap.current_animation_length,0.1) if ap else 0)
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/idle_%d.png" % idx)
	# force a gesture on the current character
	ls.set("gesture_timer", 0.0)
	await create_timer(0.6).timeout
	var ap2 = ls.get("actor_anim")
	print("GESTURE now=", ap2.current_animation if ap2 else "none", " clip=", ls.get("gesture_clip"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/gesture.png")
	print("GEST_DONE")
	quit()
