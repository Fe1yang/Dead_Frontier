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
	await create_timer(0.2).timeout
	main.get("owned_vehicles").append("GOLD_CAR") if main.get("owned_vehicles") is Array else null
	main.set("loadout_on", true); main.set("owned_vehicle", "GOLD_CAR")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.8).timeout
	var p = main.get("player")
	print("vehicle=", p.get("vehicle"), " speed=", p.call("vehicle_speed"), " ram=", p.call("vehicle_ram"))
	var box := AABB(); var first := true
	var vm = p.get("vehicle_model")
	if vm != null:
		for mi in vm.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("car aabb size=", box.size)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/gold_car.png")
	print("GOLDCAR_DONE")
	quit()
