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
	await create_timer(0.3).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	var kinds := []
	for z in (main.get("zombies") as Array):
		if is_instance_valid(z): kinds.append(String(z.get("kind")))
	print("INTRO_KINDS ", kinds)
	var ch = main.get("chaser")
	if ch != null:
		var box := AABB(); var first := true
		for mi in ch.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("CHASER_SIZE ", box.size)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/intro_check.png")
	print("INTRO_DONE")
	quit()
