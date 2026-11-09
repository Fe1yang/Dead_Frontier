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
	await create_timer(0.4).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	print("start range_end=", main.get("vehicle_range_end"), " distance=", snappedf(main.get("distance"),1))
	main.set("distance", 970.0)
	p.call("mount_vehicle", "BIKE")
	p.set("vehicle_durability", 4.0)
	main.call("_refuel")
	print("after fuel: durability=", snappedf(p.get("vehicle_durability"),1), " range_end=", main.get("vehicle_range_end"), " (expect 1970)")
	print("FUEL_DONE")
	quit()
