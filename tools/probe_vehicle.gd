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
	main.set("owned_vehicle", "SEDAN")
	main.call("enter_lobby")
	await create_timer(0.8).timeout
	main.call("set_lobby_tab", 2)
	await create_timer(1.0).timeout
	var ls = main.get("lobby")
	var a = ls.get("actor"); var b = ls.get("bike")
	print("actor_visible=", a.visible if a else "none", " bike_visible=", b.visible if b else "none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/vehicle_tab.png")
	print("VEH_DONE")
	quit()
