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
	var asset: String = String(lobby.CHARACTERS[idx].asset)

	var hud = main.get("hud")
	if hud != null:
		hud.visible = false

	lobby.call("show_character", idx, asset)
	await create_timer(1.0).timeout

	var actor = lobby.get("actor")
	var origin: Vector3 = lobby.ORIGIN
	var stand_local: Vector3 = lobby.get("STAND")
	var spot := origin + Vector3(stand_local.x, 0.0, stand_local.z)
	if is_instance_valid(actor):
		actor.global_position = spot
		actor.rotation.y = 0.0
		actor.visible = true

	# whatever camera the lobby is actually rendering with
	var cam3d := root.get_viewport().get_camera_3d()
	print("ACTIVE CAM ", cam3d.name if cam3d != null else "none")
	if cam3d != null:
		var cam_pos := Vector3(spot.x, spot.y + 1.55, spot.z + 1.0)
		cam3d.global_position = cam_pos
		cam3d.look_at(Vector3(spot.x, spot.y + 1.44, spot.z), Vector3.UP)
		cam3d.fov = 30.0
		print("CAM moved to ", cam3d.global_position)
	RenderingServer.force_draw(false)
	root.get_viewport().get_texture().get_image().save_png(out_path)
	print("SHOT ", out_path)
	print("PORTRAIT_DONE")
	quit()
