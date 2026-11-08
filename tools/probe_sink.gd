extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _measure(z, clip: String) -> float:
	var ap = z.find_child("AnimationPlayer", true, false)
	ap.play(clip); ap.seek(0.3, true)
	await process_frame
	await process_frame
	var lo := 1.0e9
	for mi in z.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = mi.global_transform * mi.get_aabb()
		lo = minf(lo, b.position.y)
	return lo
func _run() -> void:
	var scene = load("res://assets/models/actors/zombie_walker_universal.glb")
	var z = scene.instantiate()
	root.add_child(z)
	await process_frame
	var ap = z.find_child("AnimationPlayer", true, false)
	print("CLIPS ", ap.get_animation_list())
	for clip in ["Zombie_Walk_Fwd", "Death01"]:
		print("MIN_Y ", clip, " = ", snappedf(await _measure(z, clip), 0.001))
	var lib = load("res://assets/animation-library/ual1/UAL1_Standard.glb").instantiate()
	var sk: Skeleton3D = lib.find_children("*", "Skeleton3D", true, false)[0]
	var hips: int = sk.find_bone("pelvis")
	print("UAL1 pelvis rest=", sk.get_bone_rest(hips).origin)
	var dz: Skeleton3D = z.find_children("*", "Skeleton3D", true, false)[0]
	var dh: int = dz.find_bone("pelvis")
	print("ZOMBIE pelvis rest=", dz.get_bone_rest(dh).origin)
	print("SINK_DONE")
	quit()
