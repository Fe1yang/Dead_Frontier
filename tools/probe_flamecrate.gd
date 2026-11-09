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
	await create_timer(0.6).timeout
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	main.call("_spawn_pickup", "ammo", -6.0)
	await create_timer(0.4).timeout
	# put a crate right in front and hose it
	var crate = (load("res://scripts/weapon_crate_3d.gd") as GDScript).new()
	crate.call("setup", "SMG", 4)
	crate.position = Vector3(0, 0, -4.0)
	main.add_child(crate)
	(main.get("crates") as Array).append(crate)
	await create_timer(0.3).timeout
	var before: int = crate.hits_left
	for i in range(4):
		main.call("_fire")
		await create_timer(0.1).timeout
	print("crate hits ", before, " -> ", crate.hits_left)
	var jet = p.get("flame_jet")
	print("flame jet valid=", is_instance_valid(jet), " emitting=", jet.emitting if is_instance_valid(jet) else false)
	print("FC_DONE")
	quit()
