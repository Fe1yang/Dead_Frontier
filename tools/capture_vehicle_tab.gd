extends SceneTree
## Capture the lobby 载具 tab (gold bike selected) into tools/vehicle_tab.png.
## Run: Godot_v4.7.2-stable_win64_console.exe --path . -s tools/capture_vehicle_tab.gd

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	var main := current_scene
	if main == null:
		push_error("capture: no main scene")
		quit(1)
		return
	await create_timer(1.2).timeout
	# The boot-trace card pauses the tree; a paused lobby never runs _process.
	paused = false
	await create_timer(2.6).timeout
	paused = false
	# The cover swallows an early enter_lobby(); keep knocking until the lobby wins.
	for _i in range(8):
		if String(main.get("state")) == "character_select":
			break
		main.enter_lobby()
		await create_timer(0.4).timeout
	print("STATE_NOW ", main.get("state"))
	await create_timer(0.3).timeout
	main.set_lobby_tab(3)
	main.set("vehicle_choice", 3)
	var lobby: Node = main.get("lobby")
	if lobby and lobby.has_method("set_vehicle_visual"):
		lobby.call("set_vehicle_visual", 3)
	await create_timer(1.8).timeout
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://tools/vehicle_tab.png")
	print("CAPTURE_OK ", img.get_width(), "x", img.get_height())
	quit()
