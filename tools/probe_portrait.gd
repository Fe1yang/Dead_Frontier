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
	await create_timer(0.8).timeout
	var idx := int(OS.get_environment("CHAR_INDEX"))
	var out_path := String(OS.get_environment("SHOT_OUT"))
	var lobby = main.get("lobby")
	lobby.call("show_character", idx, "")
	await create_timer(0.6).timeout
	# straight-on, chest height, tight: head to chest fills the frame
	var stand: Vector3 = lobby.get("STAND")
	var cam := Vector3(stand.x, 1.55, stand.z + 3.6)
	main.call("debug_camera_at", cam, Vector3(stand.x, 1.40, stand.z), 26.0)
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png(out_path)
	print("SHOT ", out_path)
	print("PORTRAIT_DONE")
	quit()
