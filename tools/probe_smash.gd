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
	main.call("_spawn_barrel")
	main.call("_spawn_crates")
	await create_timer(0.4).timeout
	var barrel = null
	for b in (main.get("barrels") as Array):
		if is_instance_valid(b) and not b.get("dead"): barrel = b; break
	var crate = null
	for c in (main.get("crates") as Array):
		if is_instance_valid(c) and not c.get("broken"): crate = c; break
	print("BEFORE barrels=", (main.get("barrels") as Array).size(), " crates=", (main.get("crates") as Array).size(), " weapon=", main.get("player").get("weapon"))
	if barrel != null:
		barrel.position = Vector3(0.0, 0.0, -2.0)
		main.get("player").position = Vector3(0.0, 0.0, -1.7)
		main.call("_vehicle_smash")
		await create_timer(0.12).timeout
		print("BARREL dead=", barrel.get("dead") if is_instance_valid(barrel) else "freed", " barrels_left=", (main.get("barrels") as Array).size())
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/smash_barrel.png")
		print("SHOT barrel")
	if crate != null:
		crate.position = Vector3(0.0, 0.0, -1.0)
		main.get("player").position = Vector3(0.0, 0.0, 0.0)
		var before: String = main.get("player").get("weapon")
		main.call("_vehicle_smash")
		await create_timer(0.2).timeout
		print("CRATE broken=", crate.get("broken"), " weapon ", before, " -> ", main.get("player").get("weapon"))
	print("SMASH_DONE")
	quit()
