extends SceneTree
func _initialize() -> void:
	call_deferred("inspect_actor")
func inspect_actor() -> void:
	var actor=load("res://assets/models/actors/survivor_male_universal.glb").instantiate()
	root.add_child(actor)
	var animation=actor.find_child("AnimationPlayer",true,false) as AnimationPlayer
	if animation: animation.play("Run_Gun")
	await process_frame
	await process_frame
	var skeleton=actor.find_child("Skeleton3D",true,false) as Skeleton3D
	print("skeleton transform=",skeleton.transform)
	for name in ["root","pelvis","spine_03","hand_r","hand_l","Head","foot_r"]:
		var index=skeleton.find_bone(name)
		if index>=0: print(name," index=",index," pose=",skeleton.get_bone_global_pose(index))
	actor.queue_free()
	await process_frame
	quit()
