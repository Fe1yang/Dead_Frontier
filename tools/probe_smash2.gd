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
	main.call("_spawn_crates")
	await create_timer(0.3).timeout
	var crate = null
	for c in (main.get("crates") as Array):
		if is_instance_valid(c) and not c.get("broken"): crate = c; break
	if crate != null:
		crate.position = Vector3(0.0, 0.0, -6.0)
		main.call("_vehicle_smash")
		await create_timer(0.05).timeout
		print("FAR (6 m ahead): broken=", crate.get("broken"), "  <- must be false")
		crate.position = Vector3(0.0, 0.0, -3.0)
		var fx_before: int = (main.get("effects") as Array).size()
		main.call("_vehicle_smash")
		await create_timer(0.05).timeout
		print("TOUCH (3 m, under the nose): broken=", crate.get("broken"), "  <- must be true")
	main.call("_spawn_barrel")
	await create_timer(0.25).timeout
	var barrel = null
	for b in (main.get("barrels") as Array):
		if is_instance_valid(b) and not b.get("dead"): barrel = b; break
	if barrel != null:
		barrel.position = Vector3(0.0, 0.0, -3.0)
		var before: int = (main.get("effects") as Array).size()
		main.call("_vehicle_smash")
		await create_timer(0.08).timeout
		print("BARREL pieces spawned=", (main.get("effects") as Array).size() - before, " dead=", not is_instance_valid(barrel) or barrel.get("dead"))
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/smash_now.png")
		print("SHOT smash")
	print("SMASH2_DONE")
	quit()
