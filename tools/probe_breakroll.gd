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
	main.set("owned_vehicle", ""); main.set("loadout_on", false)
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
	r.position = Vector3(0.0, 0.0, -6.0)
	await create_timer(0.05).timeout
	var z0: float = r.position.z
	main.call("_break_crate", r)
	var samples := []
	for i in range(4):
		await create_timer(0.15).timeout
		samples.append(snappedf(r.position.z - z0, 0.01) if is_instance_valid(r) else 99.0)
	print("BROKEN barrel dz per 0.15s = ", samples, "  (all positive = rides the road, no backwards roll)")
	print("BREAKROLL_DONE")
	quit()
