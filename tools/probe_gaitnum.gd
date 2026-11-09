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
	var owned = main.get("owned_pets")
	owned[5] = true
	main.set("pet_choice", 5); main.set("pet_equipped", true); main.set("loadout_on", true)
	main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(1.5).timeout
	var pets = main.get("companion_pets")
	if pets.size() > 0:
		var g = pets[0].get("gallop")
		if g != null:
			print("GAIT leg_len=%.2f stride_len=%.2f stride=%.3f" % [g.call("leg_length"), g.call("stride_length"), g.get("stride")])
			print("GAIT stride@3.5=%.3f  @5.0=%.3f" % [g.call("stride_for_speed",3.5), g.call("stride_for_speed",5.0)])
	print("GAITNUM_DONE")
	quit()
