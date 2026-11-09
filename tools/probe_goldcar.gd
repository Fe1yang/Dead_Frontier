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
	main.set("owned_vehicle", "GOLD_CAR")
	main.set("vehicle_equipped", true)
	main.set("loadout_on", true)
	main.call("start_run", true, true)
	await create_timer(0.8).timeout
	print("range_end=", main.get("vehicle_range_end"), " mounted=", main.get("player").get("vehicle"))
	var p = main.get("player")
	print("speed=", p.call("vehicle_speed") if p.has_method("vehicle_speed") else "n/a")
	print("GOLDCAR_DONE")
	quit()
