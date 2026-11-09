extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.5).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	var crates = main.get("crates")
	main.call("_spawn_crates")
	await create_timer(0.5).timeout
	var c = (main.get("crates") as Array)
	var before := (main.get("weapons_owned") as Array).size() if main.get("weapons_owned") != null else 0
	var weapon_before = p.get("weapon")
	for i in range(3):
		main.call("_fire_flame")
		await create_timer(0.15).timeout
	await create_timer(0.6).timeout
	print("PLAYER_WEAPON before=", weapon_before, " after=", p.get("weapon"), " stowed=", p.get("stowed"))
	print("FLAMECRATE_DONE")
	quit()
