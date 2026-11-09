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
	main.call("open_shop")
	await create_timer(1.0).timeout
	main.call("open_armory")
	await create_timer(0.6).timeout
	var model = main.get("armory_model")
	var before: float = model.rotation.y
	# press inside the 3D area, drag right, release
	main.call("_pointer_down", Vector2(270, 340))
	for i in range(10):
		var ev := InputEventScreenDrag.new()
		ev.relative = Vector2(12, 0)
		ev.position = Vector2(270 + i * 12, 340)
		Input.parse_input_event(ev)
		await process_frame
	await create_timer(0.2).timeout
	var after: float = model.rotation.y
	print("SPIN before=", snappedf(before, 0.01), " after=", snappedf(after, 0.01), " drag=", main.get("armory_drag"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/armory_drag.png")
	print("DRAG_DONE")
	quit()
