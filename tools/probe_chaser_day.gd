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
	await create_timer(0.5).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", false, true)
	await create_timer(1.4).timeout
	main.call("set_weather", "clear")
	main.set("night_amount", 0.0)
	if main.has_method("set_night"):
		main.call("set_night", 0.0)
	await create_timer(1.2).timeout
	var ch = main.get("chaser")
	if ch:
		var box = AABB(); var first := true
		for m in ch.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print("CHASER size=", Vector3(snappedf(box.size.x,0.01),snappedf(box.size.y,0.01),snappedf(box.size.z,0.01)))
	# look at him from the front-left, chest height
	var p = ch.position if ch else Vector3.ZERO
	main.call("debug_camera_at", Vector3(p.x - 3.2, 1.9, p.z + 4.2), Vector3(p.x, 1.5, p.z), 55.0)
	await create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/chaser_day.png")
	print("CH_DAY_DONE")
	quit()
