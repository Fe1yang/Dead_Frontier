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
	await create_timer(0.4).timeout
	main.set("spawn_timer", 1.0e9)
	for idx in [0, 1]:
		var p = main.get("player")
		p.call("set_character", idx)
		p.call("reset")
		await create_timer(0.4).timeout
		main.call("_spawn_zombie", -9.0, "walker")
		await create_timer(0.9).timeout
		var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
		var hr = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
		var wm = p.get("weapon_model")
		print("CHAR ", idx, " hand_r_y=%.2f gun_y=%.2f" % [hr.y, wm.global_position.y if wm else -1.0])
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://tools/aim_%d.png" % idx)
	print("AIM_DONE")
	quit()
