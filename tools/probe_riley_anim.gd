extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var s = load("res://assets/models/actors/survivor_riley_universal.glb").instantiate()
	root.add_child(s)
	await process_frame
	var ap: AnimationPlayer = s.find_child("AnimationPlayer", true, false)
	print("AP=", ap != null)
	if ap == null: quit(); return
	print("clips=", ap.get_animation_list(), " root_node=", ap.root_node)
	for name in ap.get_animation_list():
		var a: Animation = ap.get_animation(String(name))
		print("CLIP ", name, " tracks=", a.get_track_count(), " len=", snappedf(a.length,0.01))
		if a.get_track_count() > 0:
			var p := str(a.track_get_path(0))
			print("   first track: ", p)
	ap.play("Run_Gun")
	await create_timer(0.3).timeout
	print("playing=", ap.current_animation, " pos=", snappedf(ap.current_animation_position,0.01))
	var sk: Skeleton3D = s.find_children("*", "Skeleton3D", true, false)[0]
	print("skeleton=", sk.name, " bones=", sk.get_bone_count())
	print("pelvis pose y=", snappedf(sk.get_bone_global_pose(sk.find_bone("pelvis")).origin.y,0.001))
	print("RILEYANIM_DONE")
	quit()
