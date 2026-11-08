extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _pelvis_y(z, clip: String) -> float:
	var ap: AnimationPlayer = z.find_child("AnimationPlayer", true, false)
	ap.play(clip); ap.seek(0.4, true)
	await process_frame
	await process_frame
	var sk: Skeleton3D = z.find_children("*", "Skeleton3D", true, false)[0]
	var i: int = sk.find_bone("pelvis")
	return sk.get_bone_global_pose(i).origin.y
func _run() -> void:
	var z = load("res://assets/models/actors/zombie_walker_universal.glb").instantiate()
	root.add_child(z)
	await process_frame
	var ap: AnimationPlayer = z.find_child("AnimationPlayer", true, false)
	for clip in ap.get_animation_list():
		print("PELVIS ", clip, " y=", snappedf(await _pelvis_y(z, String(clip)), 0.001))
	print("HIP2_DONE")
	quit()
