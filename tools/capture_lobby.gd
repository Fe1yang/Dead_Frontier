extends SceneTree
## Tiny capture harness: open the lobby, let the set settle, save one frame, quit.
## Run from the project root with:
##   Godot_v4.7.2-stable_win64_console.exe --path . --script tools/capture_lobby.gd

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(8):
		await process_frame
	var main := current_scene
	if main == null:
		push_error("capture: no main scene")
		quit(1)
		return
	if main.has_method("enter_lobby"):
		main.enter_lobby()
	if main.has_method("select_character"):
		main.select_character(0)
	await create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://tools/lobby_capture.png")
	print("CAPTURE_OK ", img.get_width(), "x", img.get_height())
	quit()
