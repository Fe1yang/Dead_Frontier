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
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.3).timeout
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_chase_begin")
	await create_timer(0.9).timeout
	var ch = main.get("chaser")
	if ch == null:
		print("NO_CHASER"); quit(); return
	var box := AABB(); var first := true
	for mi in ch.find_children("*","MeshInstance3D",true,false):
		var m: MeshInstance3D = mi
		if m.mesh == null: continue
		var b: AABB = m.global_transform * m.get_aabb()
		box = b if first else box.merge(b)
		first = false
	var center: Vector3 = box.get_center()
	var span: float = maxf(box.size.x, maxf(box.size.y, box.size.z))
	var cam := Camera3D.new(); cam.fov=45.0
	main.add_child(cam); cam.make_current()
	cam.position = center + Vector3(span*0.55, span*0.30, -span*1.9)
	cam.look_at(center)
	await create_timer(0.35).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pursuer_chase3.png")
	print("SHOT3_DONE size=", box.size, " pos=", ch.position)
	quit()
