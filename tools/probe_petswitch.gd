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
	main.call("set_lobby_tab", 1)
	await create_timer(0.4).timeout
	var ls = main.get("lobby")
	ls.call("show_pet", "res://assets/models/pets/czech_wolfdog.glb")
	await create_timer(0.8).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pet_wolf.png")
	# switch tiger -> lion quickly, the case that used to leave both on stage
	ls.call("show_pet", "res://assets/models/pets/white_tiger.glb")
	await create_timer(0.2).timeout
	ls.call("show_pet", "res://assets/models/pets/lion.glb")
	await create_timer(1.0).timeout
	var count := 0
	for c in ls.get_children():
		if c.has_meta("lobby_pet"): count += 1
	print("PETS_ON_STAGE ", count)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pet_lion_after_switch.png")
	print("PETS_DONE")
	quit()
