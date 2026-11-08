extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/gear_%s.png" % n)
	print("SHOT ", n)
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.5).timeout
	print("ON  loadout=", main.get("loadout_on"), " vehicle=", main.get("owned_vehicle"), " pet=", main.get("pet_equipped"))
	await _shot("1_on")
	main.call("_pointer_down", Vector2(36, 898))
	await create_timer(0.3).timeout
	print("OFF loadout=", main.get("loadout_on"))
	await _shot("2_off")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	print("RUN vanilla: player.vehicle='", main.get("player").get("vehicle"), "' pets=", (main.get("companion_pets") as Array).size())
	main.call("_pointer_down", Vector2(36, 898))
	await create_timer(0.2).timeout
	print("back ON loadout=", main.get("loadout_on"))
	print("GEAR_DONE")
	quit()
