extends SceneTree
const OUTPUT_DIR := "C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/diagnostics/grip-restored"
const TACTICAL := "res://assets/models/actors/survivor_maya_tactical_universal.glb"

func _initialize() -> void:
	call_deferred("_run")

func _capture(path: String, player: Node3D) -> void:
	await process_frame
	player._update_weapon_transform()
	await RenderingServer.frame_post_draw
	print("FORMAL_CAPTURE ",path," result=",root.get_texture().get_image().save_png(path))

func _bone_lengths(player: Node3D, label: String) -> void:
	var sk: Skeleton3D=player.skeleton
	for side in ["r","l"]:
		var upper:=sk.find_bone("upperarm_"+side)
		var lower:=sk.find_bone("lowerarm_"+side)
		var hand:=sk.find_bone("hand_"+side)
		var rest_upper:=sk.get_bone_global_rest(upper).origin.distance_to(sk.get_bone_global_rest(lower).origin)
		var rest_lower:=sk.get_bone_global_rest(lower).origin.distance_to(sk.get_bone_global_rest(hand).origin)
		var posed_upper:=sk.get_bone_global_pose(upper).origin.distance_to(sk.get_bone_global_pose(lower).origin)
		var posed_lower:=sk.get_bone_global_pose(lower).origin.distance_to(sk.get_bone_global_pose(hand).origin)
		print("FORMAL_BONE_LENGTH ",label," ",side," upper=",posed_upper,"/",rest_upper," forearm=",posed_lower,"/",rest_lower)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game=load("res://scenes/main.tscn").instantiate()
	root.add_child(game)
	await process_frame
	game.sound.muted=true
	game.pet_equipped=false
	game._begin_intro()
	await create_timer(0.8).timeout
	game.set_process(false)
	game.set_physics_process(false)
	game.hud.visible=false
	var variants := [
		{"label":"mason","char":0,"asset":""},
		{"label":"riley","char":1,"asset":""},
		{"label":"darius","char":2,"asset":""},
		{"label":"maya","char":3,"asset":""},
		{"label":"maya-tactical","char":3,"asset":TACTICAL},
	]
	for v in variants:
		var player=game.player
		player.set_character(v.char,v.asset)
		print("FORMAL_MODEL ",v.label," source=",player.model.scene_file_path," override=",v.asset)
		print("FORMAL_CLIP ",v.label," resolved=",player.run_clip," playing=",player.animation_player.current_animation)
		await create_timer(0.25).timeout
		_bone_lengths(player,v.label)
		for phase in range(2):
			var camera: Camera3D=game.camera
			camera.fov=42
			camera.h_offset=0
			camera.v_offset=0
			var center: Vector3=player.global_position+Vector3(0,1.15,0)
			camera.global_position=player.global_position+Vector3(0,1.55,-2.65)
			camera.look_at(center)
			await _capture(OUTPUT_DIR+"/"+v.label+"-"+str(phase)+"-front.png",player)
			camera.global_position=player.global_position+Vector3(2.35,1.50,-1.20)
			camera.look_at(center)
			await _capture(OUTPUT_DIR+"/"+v.label+"-"+str(phase)+"-side.png",player)
			await create_timer(0.24).timeout
	game.queue_free()
	await process_frame
	await process_frame
	quit()
