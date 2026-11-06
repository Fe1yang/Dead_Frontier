extends SceneTree
## Face close-ups two seconds apart: with the blink lids removed, both shots must show open eyes.

func _initialize() -> void:
	call_deferred("_run")

func _head_position(actor: Node3D) -> Vector3:
	var skeleton:=actor.find_child("Skeleton3D",true,false) as Skeleton3D
	if skeleton:
		var head:=skeleton.find_bone("Head")
		if head>=0:
			return skeleton.global_transform*skeleton.get_bone_global_pose(head).origin
	return actor.global_position+Vector3(0,1.62,0)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/blink"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.go_to_lobby(); await create_timer(0.4).timeout
	var head:=_head_position(game.lobby.actor)
	game.camera.position=head+Vector3(0,0.015,0.56); game.camera.fov=31.0
	game.camera.look_at(head+Vector3(0,-0.035,0))
	for i in range(2):
		await create_timer(2.0).timeout
		await RenderingServer.frame_post_draw
		var path: String="res://diagnostics/blink/face-%d.png"%i
		assert(root.get_texture().get_image().save_png(path)==OK)
		print("FACE_CAPTURE ",path)
	print("FACE_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
