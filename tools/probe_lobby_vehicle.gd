extends SceneTree
## Where does the lobby bike land on screen, and does the card band cover it?

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var game: Node3D = (load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.call("_clear_world")
	game.call("enter_lobby")
	await create_timer(0.5).timeout
	game.call("set_lobby_tab", 3)
	await create_timer(0.4).timeout
	var lobby: Node = game.get("lobby")
	var bike: Node3D = lobby.get("bike") as Node3D
	var cam: Camera3D = game.get("camera") as Camera3D
	print("STATE=", game.get("state"), " focus=", lobby.get("focus_vehicle"))
	print("BAND_TOP=", game.get("LOBBY_BAND_TOP"), " ui_h=", game.get("ui_h"))
	print("CAM=", cam.global_position, " fov=", cam.fov)
	if is_instance_valid(bike):
		print("BIKE visible=", bike.visible, " pos=", bike.global_position, " scale=", bike.scale.x)
		var box := AABB()
		var first := true
		for mi in bike.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("BIKE world aabb pos=", box.position, " size=", box.size)
		var bottom := cam.unproject_position(box.position)
		var top := cam.unproject_position(Vector3(box.position.x, box.position.y + box.size.y, box.position.z))
		print("SCREEN bottom=", bottom, " top=", top)
		print("VISIBLE_ABOVE_BAND=", top.y < float(game.get("LOBBY_BAND_TOP")))
	print("LOBBY_PROBE_DONE")
	game.queue_free()
	await process_frame
	quit()
