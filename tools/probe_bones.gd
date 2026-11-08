extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var scene = load("res://assets/models/actors/survivor_jian_scout_universal.glb").instantiate()
	root.add_child(scene)
	await process_frame
	var sk: Skeleton3D = scene.find_children("*", "Skeleton3D", true, false)[0]
	var names := []
	for i in range(sk.get_bone_count()):
		names.append(sk.get_bone_name(i))
	print("BONES(", sk.get_bone_count(), "): ", ", ".join(names))
	print("BONES_DONE")
	quit()
