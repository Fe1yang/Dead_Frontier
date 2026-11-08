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
	await create_timer(0.5).timeout
	main.call("set_lobby_tab", 0)
	var ls = main.get("lobby")
	for idx in [0, 1, 3, 4]:
		main.call("_lobby_tap", (main.call("lobby_card_rect", idx) as Rect2).get_center())
		await create_timer(0.9).timeout
		var flag = ls.get("lobby_has_clip_idle")
		var ap = ls.get("actor_anim")
		print("CHAR ", idx, " clip_idle=", flag, " anim=", ap.current_animation if ap else "none", " playing=", ap.is_playing() if ap else false)
	print("LI_DONE")
	quit()
