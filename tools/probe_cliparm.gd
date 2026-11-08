extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _measure(path: String) -> void:
	var s = load(path).instantiate()
	root.add_child(s)
	await process_frame
	var ap: AnimationPlayer = s.find_child("AnimationPlayer", true, false)
	var sk: Skeleton3D = s.find_children("*", "Skeleton3D", true, false)[0]
	if ap == null:
		print(path, " no anim"); s.queue_free(); return
	var clip := "Run_Gun"
	for c in ap.get_animation_list():
		if String(c).begins_with("Run_Gun"):
			clip = String(c); break
	ap.play(clip)
	ap.seek(0.35, true)
	await process_frame
	await process_frame
	var hr: Vector3 = sk.get_bone_global_pose(sk.find_bone("hand_r")).origin
	var sh: Vector3 = sk.get_bone_global_pose(sk.find_bone("upperarm_r")).origin
	print("%-28s clip=%-16s hand_y=%.2f shoulder_y=%.2f  dz=%.2f" % [path.get_file(), clip, hr.y, sh.y, hr.z - sh.z])
	s.queue_free()
func _run() -> void:
	await _measure("res://assets/models/actors/survivor_medic_universal.glb")
	await _measure("res://assets/models/actors/survivor_riley_universal.glb")
	await _measure("res://assets/models/actors/survivor_maya_universal.glb")
	print("CLIPARM_DONE")
	quit()
