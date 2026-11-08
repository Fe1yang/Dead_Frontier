extends SceneTree
## Sedan check: lobby card, store row, and the car actually mounted in a run.
## Run: godot --path <project> --script res://tools/probe_sedan.gd

var main: Node

func _initialize() -> void:
	call_deferred("_run")

func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/sedan_%s.png" % name)
	print("SHOT ", name)

func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.call("set_lobby_tab", 3)
	await create_timer(0.8).timeout
	print("vehicle cards=", main.call("lobby_item_count"))
	await _shot("1_lobby")
	# store, scrolled to the vehicles
	main.call("open_store")
	await create_timer(0.4).timeout
	for it in main.call("store_layout"):
		if it.has("header") and String(it.header) == "vehicle":
			main.set("store_scroll", maxf(0.0, (it.rect as Rect2).position.y - 150.0))
			break
	await create_timer(0.6).timeout
	var found := false
	for it in main.call("store_layout"):
		if it.has("pack") and String(it.pack.get("id","")) == "vehicle_sedan":
			found = true
			print("STORE sedan row rect=", main.call("store_screen_rect", it), " price=", main.call("pack_price", it.pack, "USD"))
	await _shot("2_store")
	print("STORE_HAS_SEDAN=", found)
	# into a run and sit in the car
	main.call("close_store")
	await create_timer(0.3).timeout
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("dismount_vehicle")
	await create_timer(0.2).timeout
	p.call("mount_vehicle", "SEDAN")
	await create_timer(0.4).timeout
	print("MOUNTED vehicle=", p.get("vehicle"), " rider_visible=", p.get("model").visible)
	var box := AABB()
	var first := true
	for mi in p.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = mi.global_transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	print("PLAYER+CAR aabb size=", box.size)
	var vm = p.get("vehicle_model")
	var vbox := AABB()
	var vfirst := true
	for mi in vm.find_children("*", "MeshInstance3D", true, false):
		var b2: AABB = mi.global_transform * mi.get_aabb()
		vbox = b2 if vfirst else vbox.merge(b2)
		vfirst = false
	print("CAR MODEL aabb size=", vbox.size, " min_y=", snappedf(vbox.position.y, 0.01))
	await create_timer(0.3).timeout
	await _shot("3_inrun")
	print("SEDAN_DONE")
	quit()
