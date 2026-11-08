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
	await create_timer(0.5).timeout
	var p = main.get("player")
	for idx in [0,1,2,3,4]:
		p.call("set_character", idx)
		p.call("reset")
		await create_timer(0.45).timeout
		var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
		var wm: Node3D = p.get("weapon_model")
		var hr: Vector3 = sk.global_transform * sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
		var d: float = wm.global_position.distance_to(hr) if wm != null else -1.0
		print("CHAR ", idx, " gun->handR = %.2f m  root_skel=%s" % [d, sk.get_parent().name])
	print("GUNHAND2_DONE")
	quit()
