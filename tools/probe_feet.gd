extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var z = load("res://assets/models/actors/zombie_walker_universal.glb").instantiate()
	root.add_child(z)
	await process_frame
	var ap: AnimationPlayer = z.find_child("AnimationPlayer", true, false)
	var sk: Skeleton3D = z.find_children("*", "Skeleton3D", true, false)[0]
	var names := []
	for i in range(sk.get_bone_count()):
		names.append(sk.get_bone_name(i))
	print("BONES_TAIL ", names.slice(names.size()-6, names.size()))
	ap.play("Zombie_Walk_Fwd")
	for t in [0.0, 0.3, 0.6, 0.9]:
		ap.seek(t, true)
		await process_frame
		await process_frame
		var lo := 1.0e9
		var lo_name := ""
		for i in range(sk.get_bone_count()):
			var y: float = sk.get_bone_global_pose(i).origin.y
			var n := sk.get_bone_name(i)
			if n.contains("foot") or n.contains("toe") or n.contains("ball"):
				if y < lo: lo = y; lo_name = n
		print("T=", t, " lowest foot bone ", lo_name, " y=", snappedf(lo, 0.001))
	print("FEET_DONE")
	quit()
