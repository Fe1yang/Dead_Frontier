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
	for idx in [0, 1, 3]:
		var p = main.get("player")
		p.call("set_character", idx)
		p.call("reset")
		await create_timer(0.5).timeout
		main.call("_spawn_zombie", -9.0, "walker")
		await create_timer(0.8).timeout
		var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
		var hr: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
		var sh: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("upperarm_r")).origin
		print("CHAR %d  hand_y=%.2f  forward_dz=%.2f  side_dx=%.2f" % [idx, hr.y, hr.z - sh.z, absf(hr.x - sh.x)])
	print("HANDREL_DONE")
	quit()
