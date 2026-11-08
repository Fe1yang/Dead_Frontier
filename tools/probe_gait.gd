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
	owned[4] = true; owned[5] = true
	main.set("loadout_on", true)
	main.set("owned_vehicle", "")
	for who in [4, 5]:
		main.set("pet_choice", who)
		main.set("pet_equipped", true)
		main.call("enter_lobby")
		await create_timer(0.4).timeout
		main.call("start_run", true, true)
		await create_timer(0.4).timeout
		if String(main.get("state")) == "intro":
			main.call("_finish_intro")
		await create_timer(1.8).timeout
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/gait_%d.png" % who)
		main.call("enter_lobby")
		await create_timer(0.5).timeout
	print("GAIT_DONE")
	quit()
