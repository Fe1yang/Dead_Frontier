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
	var ls = main.get("lobby")
	ls.call("show_pet", "res://assets/models/pets/white_tiger.glb")
	await create_timer(0.8).timeout
	var pet = ls.get("pet")
	for deg in [0.0, -90.0, 180.0]:
		pet.rotation.y = deg_to_rad(deg)
		await create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/tiger_%d.png" % int(deg))
	print("PETYAWS_DONE")
	quit()
