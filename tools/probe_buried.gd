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
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	for i in range(3):
		main.call("_spawn_zombie", -4.0 - float(i)*2.0, "walker")
	await create_timer(0.6).timeout
	for q in (main.get("zombies") as Array):
		if not is_instance_valid(q): continue
		var mdl = q.get("model")
		var sk: Skeleton3D = q.find_children("*", "Skeleton3D", true, false)[0]
		var bi: int = sk.find_bone("ball_leaf_r")
		var gy: float = (sk.global_transform * sk.get_bone_global_pose(bi)).origin.y
		print("Z pos=", q.position, " model_pos=", mdl.position, " model_scale=", mdl.scale, " foot_world_y=", snappedf(gy, 0.001))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/buried.png")
	print("BURIED_DONE")
	quit()
