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
	main.call("_spawn_zombie", -6.0, "jockey")
	await create_timer(1.0).timeout
	var z = (main.get("zombies") as Array).back()
	for ap in z.find_children("*", "AnimationPlayer", true, false):
		var clips := (ap as AnimationPlayer).get_animation_list()
		print("PLAYER ", ap.name, " current=", (ap as AnimationPlayer).current_animation, " clips=", clips)
	print("JOCKEY2_DONE")
	quit()
