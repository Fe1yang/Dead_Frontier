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
	main.set("character_choice", 1)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -9.0, "walker")
	var p = main.get("player")
	var sk: Skeleton3D = p.find_children("*", "Skeleton3D", true, false)[0]
	var ap: AnimationPlayer = p.find_child("AnimationPlayer", true, false)
	print("PLAYER clip=", ap.current_animation if ap else "none", " playing=", ap.is_playing() if ap else false)
	var b = sk.find_bone("upperarm_r")
	var q1 = sk.get_bone_pose_rotation(b)
	await create_timer(0.35).timeout
	var q2 = sk.get_bone_pose_rotation(b)
	print("BONE_DELTA deg=", snappedf(rad_to_deg(q1.angle_to(q2)), 0.1))
	var hb = sk.find_bone("thigh_l")
	var t1 = sk.get_bone_pose_rotation(hb)
	await create_timer(0.35).timeout
	var t2 = sk.get_bone_pose_rotation(hb)
	print("THIGH_DELTA deg=", snappedf(rad_to_deg(t1.angle_to(t2)), 0.1))
	print("CLIP after=", ap.current_animation if ap else "none")
	print("RUNANIM_DONE")
	quit()
