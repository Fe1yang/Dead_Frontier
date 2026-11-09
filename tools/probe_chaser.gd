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
	var ch = main.get("chaser")
	if ch:
		var box = AABB(); var first = true
		for m in ch.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print("CHASER size=", Vector3(snappedf(box.size.x,0.01),snappedf(box.size.y,0.01),snappedf(box.size.z,0.01)))
	else:
		print("CHASER none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/chaser.png")
	print("CH_DONE")
	quit()
