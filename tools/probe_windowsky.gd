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
	await create_timer(1.0).timeout
	var ls = main.get("lobby")
	var night := ls.find_child("Safe_night", true, false) as MeshInstance3D
	var glass := ls.find_child("Safe_glass", true, false) as MeshInstance3D
	print("glass_visible=", glass.visible if glass else "none")
	var wp: Vector3 = night.global_transform.origin if night else Vector3.ZERO
	print("night=", Vector3(snappedf(wp.x,0.1), snappedf(wp.y,0.1), snappedf(wp.z,0.1)))
	# aim the camera at the window so the shot shows it
	var cam: Camera3D = null
	for c in main.find_children("*", "Camera3D", true, false):
		cam = c; break
	main.call("debug_camera_at", wp + Vector3(0.0, -0.6, 3.2), wp + Vector3(0, 0.4, 0), 46.0)
	await create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/window_sky.png")
	print("WS_DONE")
	quit()
