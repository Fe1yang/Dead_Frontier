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
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9); main.set("barrel_timer", 1.0e9)
	main.call("_spawn_zombie", -7.0, "walker_c")
	main.call("_spawn_zombie", -9.5, "walker_c")
	await create_timer(0.8).timeout
	for q in (main.get("zombies") as Array):
		if not is_instance_valid(q): continue
		var sk: Skeleton3D = q.find_children("*", "Skeleton3D", true, false)[0]
		var bi: int = sk.find_bone("ball_leaf_r")
		var gy: float = (sk.global_transform * sk.get_bone_global_pose(bi)).origin.y
		var ap = q.get("animation_player")
		print("Z kind=", q.get("kind"), " clip=", ap.current_animation if ap else "none", " foot_y=", snappedf(gy, 0.01))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/walker_c.png")
	print("ASIAC_DONE")
	quit()
