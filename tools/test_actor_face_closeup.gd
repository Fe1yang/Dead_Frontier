extends SceneTree
const OUTPUT_DIR: String="C:/Users/user/Documents/kimi/tasks/2026-11-04/00-09-49-288c0219/diagnostics/actor-inspection"

func _initialize() -> void:
	call_deferred("_run")

func _head_position(actor: Node3D) -> Vector3:
	var skeleton:=actor.find_child("Skeleton3D",true,false) as Skeleton3D
	if skeleton:
		var head:=skeleton.find_bone("Head")
		if head>=0:
			return skeleton.global_transform*skeleton.get_bone_global_pose(head).origin
	return actor.global_position+Vector3(0,1.62,0)

func _capture(game: Node3D,label: String) -> void:
	await create_timer(0.35).timeout
	var head:=_head_position(game.lobby.actor)
	game.camera.position=head+Vector3(0,0.015,0.56)
	game.camera.fov=31.0
	game.camera.look_at(head+Vector3(0,-0.035,0))
	await create_timer(0.20).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/"+label+".png")==OK)
	print("FACE_CAPTURE ",label," head=",head)

func _set_normal(actor: Node3D,enabled: bool) -> void:
	for node in actor.find_children("*","MeshInstance3D",true,false):
		var mesh_node:=node as MeshInstance3D
		for surface in range(mesh_node.mesh.get_surface_count()):
			var mat:=mesh_node.get_surface_override_material(surface)
			if mat==null: mat=mesh_node.mesh.surface_get_material(surface)
			if mat is StandardMaterial3D:
				var standard:=mat as StandardMaterial3D
				print("MATERIAL normal_enabled=",standard.normal_enabled," normal_scale=",standard.normal_scale," filter=",standard.texture_filter," shading=",standard.shading_mode)
				standard.normal_enabled=enabled

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game.state="lobby"
	game.hud.visible=false
	game.lobby.visible=true
	for i in [1,2,0]:
		game.lobby.show_character(i)
		await _capture(game,"face-closeup-%d-normal"%i)
		if i==1:
			_set_normal(game.lobby.actor,false)
			await _capture(game,"face-closeup-1-no-normal")
	print("FACE_CLOSEUP_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
