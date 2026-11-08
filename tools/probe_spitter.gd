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
	await create_timer(0.35).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9); main.set("barrel_timer", 1.0e9)
	main.call("_spawn_zombie", -12.0, "spitter")
	await create_timer(0.5).timeout
	var s = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q) and String(q.get("kind"))=="spitter": s = q
	if s == null:
		print("NO SPITTER"); quit(); return
	print("SPITTER height=", s.call("collision_height"), " radius=", s.get("radius"), " hp=", s.get("health"))
	s.set("spit_timer", 0.01)
	for i in range(40):
		await create_timer(0.05).timeout
		if (main.get("venoms") as Array).size() > 0: break
	print("VENOM in flight=", (main.get("venoms") as Array).size())
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/spitter_flight.png")
	for i in range(40):
		await create_timer(0.05).timeout
		if (main.get("venoms") as Array).size() == 0: break
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/spitter_splash.png")
	print("SPITTER_DONE")
	quit()
