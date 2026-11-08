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
	await create_timer(0.4).timeout
	main.set("character_choice", 4)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -9.0, "walker")
	await create_timer(0.6).timeout
	var p = main.get("player")
	var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
	var sh: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("upperarm_r")).origin
	var fwd: Vector3 = -(sk.global_transform.basis.z)
	var right: Vector3 = sk.global_transform.basis.x
	main.call("debug_camera_at", sh + fwd * 0.85 + right * 0.55 + Vector3(0, 0.15, 0), sh, 30.0)
	await create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/shoulder.png")
	print("SH_DONE")
	quit()
