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
	main.call("_spawn_zombie", -9.0, "spitter")
	await create_timer(0.5).timeout
	var s = null
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q) and String(q.get("kind"))=="spitter": s = q
	if s == null:
		print("NO SPITTER"); quit(); return
	main.call("_start_venom_stream", s)
	await create_timer(0.35).timeout
	print("STREAMS=", (main.get("venom_streams") as Array).size())
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/vomit_stream.png")
	print("SHOT stream")
	await create_timer(1.4).timeout
	print("STREAMS after=", (main.get("venom_streams") as Array).size())
	# bike vs explosive barrel
	main.get("player").call("mount_vehicle","BIKE")
	await create_timer(0.2).timeout
	main.call("_spawn_barrel")
	await create_timer(0.2).timeout
	var b = null
	for q in (main.get("barrels") as Array):
		if is_instance_valid(q) and not q.get("dead"): b = q
	if b != null:
		b.position = Vector3(0.0, 0.0, -1.0)
		main.call("_vehicle_smash")
		await create_timer(0.05).timeout
		print("BIKE vs barrel dead=", (not is_instance_valid(b)) or b.get("dead"))
	print("SPIT2_DONE")
	quit()
