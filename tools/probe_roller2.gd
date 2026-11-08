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
	await create_timer(0.25).timeout
	var r = null
	for q in (main.get("crates") as Array):
		if is_instance_valid(q) and q.has_method("is_roller"): r = q
	if r == null:
		print("no roller"); quit(); return
	r.position = Vector3(0.0, 0.0, -3.2)
	await create_timer(0.03).timeout
	var fx_before: int = (main.get("effects") as Array).size()
	var weapon_before: String = main.get("player").get("weapon")
	main.call("_vehicle_smash")
	await create_timer(0.05).timeout
	print("ROLLER broken=", r.get("broken"), " pieces+=", (main.get("effects") as Array).size()-fx_before, " weapon ", weapon_before, "->", main.get("player").get("weapon"))
	var samples := []
	var z0: float = r.position.z if is_instance_valid(r) else 0.0
	for i in range(3):
		await create_timer(0.1).timeout
		samples.append(snappedf((r.position.z - z0) if is_instance_valid(r) else 99.0, 0.01))
	print("ROLLER dz per 0.1s = ", samples, " (positive = still going forward)")
	print("ROLLER2_DONE")
	quit()
