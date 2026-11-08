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
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	for w in ["RIFLE", "PISTOL", "SHOTGUN", "SNIPER", "LAUNCHER"]:
		p.call("set_weapon", w)
		await create_timer(0.4).timeout
		var wm = p.get("weapon_model")
		var bar: Vector3 = (wm.global_transform.basis * Vector3(0, 0, -1)).normalized()
		var aim: Vector3 = p.get("aim_direction")
		print("W ", w, " yaw=", snappedf(rad_to_deg(wm.rotation.y),1), " barrel=", Vector3(snappedf(bar.x,0.01),snappedf(bar.y,0.01),snappedf(bar.z,0.01)), " aim=", Vector3(snappedf(aim.x,0.01),snappedf(aim.y,0.01),snappedf(aim.z,0.01)), " dot=", snappedf(bar.dot(aim),0.01), " y=", snappedf(wm.global_position.y,0.01))
	print("GV_DONE")
	quit()
