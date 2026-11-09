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
	var before: bool = main.get("pet_equipped")
	main.call("_pointer_down", Vector2(453, 31))
	await create_timer(0.3).timeout
	var after: bool = main.get("pet_equipped")
	print("PET_EQUIP before=", before, " after=", after)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/gear_pet.png")
	print("GEAR_DONE")
	quit()
