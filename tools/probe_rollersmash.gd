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
	main.set("owned_vehicle", "SEDAN"); main.set("loadout_on", true)
	main.call("start_run", true, true)
	await create_timer(0.35).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9); main.set("barrel_timer", 1.0e9)
	main.call("_spawn_rollers")
	await create_timer(0.3).timeout
	var r = null
	for q in (main.get("crates") as Array):
		if is_instance_valid(q) and q.has_method("is_roller"): r = q
	if r == null:
		print("no roller"); quit(); return
	r.position = Vector3(0.0, 0.0, -2.6)
	print("roller at ", r.position, " is_roller=", r.has_method("is_roller"))
	await create_timer(0.05).timeout
	var before: int = (main.get("effects") as Array).size()
	main.call("_vehicle_smash")
	await create_timer(0.06).timeout
	print("PIECES added=", (main.get("effects") as Array).size() - before)
	for e in (main.get("effects") as Array).slice(before, (main.get("effects") as Array).size()):
		var kids := 0
		for c in e.get_children():
			if c is MeshInstance3D: kids += 1
		print("  piece node at ", e.global_position.snapped(Vector3(0.1,0.1,0.1)), " meshes=", kids, " visible=", e.visible)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/roller_smash.png")
	print("SHOT roller")
	print("ROLLERSMASH_DONE")
	quit()
