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
	main.call("set_lobby_tab", 4)
	await create_timer(0.5).timeout
	var before: bool = main.get("weapon_equipped")
	main.call("_pointer_down", Vector2(511, 31))
	await create_timer(0.3).timeout
	print("WEAPON_EQUIP before=", before, " after=", main.get("weapon_equipped"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/gear_weapon.png")
	print("GW_DONE")
	quit()
