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
	await create_timer(0.5).timeout
	# tap each pet card the way a finger would
	for i in range(5):
		var r = main.call("lobby_card_rect", i)
		main.call("_pointer_down", r.get_center())
		main.call("_pointer_up", r.get_center())
		await create_timer(0.5).timeout
	var ls = main.get("lobby")
	var animals := 0
	for c in ls.get_children():
		if c is Node3D and (c.has_meta("lobby_pet") or String(c.name).begins_with("LobbyPet")):
			animals += 1
	print("ANIMALS_AFTER_TAPS ", animals)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pet_after_taps.png")
	print("PETTAP_DONE")
	quit()
