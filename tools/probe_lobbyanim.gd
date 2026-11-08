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
	await create_timer(0.6).timeout
	main.call("set_lobby_tab", 0)
	main.call("_lobby_tap", (main.call("lobby_card_rect", 1) as Rect2).get_center())
	await create_timer(1.2).timeout
	var ls = main.get("lobby")
	var act = ls.get("actor")
	var ap: AnimationPlayer = act.find_child("AnimationPlayer", true, false)
	print("AP=", ap != null, " clip=", ap.current_animation if ap else "none")
	var anim: Animation = ap.get_animation(ap.current_animation)
	if anim:
		print("TRACKS=", anim.get_track_count())
		for i in range(min(3, anim.get_track_count())):
			print("  path: ", anim.track_get_path(i))
	var sk: Skeleton3D = act.find_children("*", "Skeleton3D", true, false)[0]
	print("SKEL_PATH=", act.get_path_to(sk))
	var b = sk.find_bone("upperarm_l")
	var q1 = sk.get_bone_pose_rotation(b)
	var p1 = sk.get_bone_global_pose(b).origin
	await create_timer(0.5).timeout
	var q2 = sk.get_bone_pose_rotation(b)
	var p2 = sk.get_bone_global_pose(b).origin
	print("ARM_ROT_DELTA deg=", snappedf(rad_to_deg(q1.angle_to(q2)),0.1), " POS_DELTA m=", snappedf(p1.distance_to(p2),0.001))
	var hb = sk.find_bone("spine_02")
	var s1 = sk.get_bone_pose_rotation(hb)
	await create_timer(0.5).timeout
	var s2 = sk.get_bone_pose_rotation(hb)
	print("SPINE_DELTA deg=", snappedf(rad_to_deg(s1.angle_to(s2)),0.1))
	print("LOBBYANIM_DONE")
	quit()
