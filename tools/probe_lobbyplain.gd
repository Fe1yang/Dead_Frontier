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
	await create_timer(1.2).timeout
	var ls = main.get("lobby")
	print("choice=", main.get("character_choice"), " asset=", main.call("character_asset", main.get("character_choice")))
	print("lobby_visible=", ls.visible, " state=", main.get("state"), " chars=", ls.CHARACTERS.size())
	ls.call("show_character", 1, "")
	await create_timer(0.8).timeout
	var a = ls.get("actor")
	print("after manual show: actor=", a != null, " visible=", a.visible if a else false)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/lobby_plain.png")
	print("PLAIN_DONE")
	quit()
