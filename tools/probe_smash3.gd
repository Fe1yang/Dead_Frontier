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
	for zpos in [-4.4, -3.9, -3.4, -2.9]:
		main.call("_spawn_crates")
		await create_timer(0.2).timeout
		var c = null
		for q in (main.get("crates") as Array):
			if is_instance_valid(q) and not q.get("broken"): c = q
		if c == null: continue
		c.position = Vector3(0.0, 0.0, zpos)
		main.call("_vehicle_smash")
		await create_timer(0.05).timeout
		print("platform centre z=", zpos, " -> broken=", c.get("broken"))
	main.call("_spawn_barrel")
	await create_timer(0.25).timeout
	var b = null
	for q in (main.get("barrels") as Array):
		if is_instance_valid(q) and not q.get("dead"): b = q
	if b != null:
		b.position = Vector3(0.0, 0.0, -3.0)
		var hp_before: float = main.get("player").get("health")
		var dur_before: float = main.get("player").get("vehicle_durability")
		main.call("_vehicle_smash")
		await create_timer(0.1).timeout
		print("EXPLOSIVE barrel dead=", (not is_instance_valid(b)) or b.get("dead"), " health ", hp_before, "->", main.get("player").get("health"), " durability ", dur_before, "->", snappedf(main.get("player").get("vehicle_durability"),0.1))
	print("SMASH3_DONE")
	quit()
