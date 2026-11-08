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
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_crates")
	await create_timer(0.3).timeout
	print("crates n=", (main.get("crates") as Array).size())
	for q in (main.get("crates") as Array):
		if not is_instance_valid(q): continue
		print("  crate z=", snappedf(q.position.z,0.01), " x=", snappedf(q.position.x,0.01), " he=", q.half_extents, " broken=", q.get("broken"))
	var c = (main.get("crates") as Array)[0]
	var cd: float = float(c.half_extents.y)
	for zpos in [-4.6, -4.2, -3.8, -3.2]:
		c.set("broken", false)
		c.position = Vector3(0.0, 0.0, zpos)
		var overlap: bool = (c.position.z+cd >= -3.72) and (c.position.z-cd <= 0.24)
		main.call("_vehicle_smash")
		await create_timer(0.02).timeout
		print("z=", zpos, " cd=", cd, " overlap_expected=", overlap, " broken_after=", c.get("broken"))
	print("BOX_DONE")
	quit()
