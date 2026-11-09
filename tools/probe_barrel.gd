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
	main.call("_spawn_barrel")
	await create_timer(0.3).timeout
	var b = (main.get("barrels") as Array).back()
	main.call("_explode", b)
	await create_timer(0.1).timeout
	await create_timer(1.6).timeout
	print("BARRELS_LEFT ", (main.get("barrels") as Array).size())
	print("BARREL_DONE")
	quit()
