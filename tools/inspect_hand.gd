extends SceneTree

func _initialize() -> void:
	call_deferred("inspect")

func inspect() -> void:
	root.size=Vector2i(1000,750)
	var scene:=Node3D.new(); root.add_child(scene)
	var environment:=WorldEnvironment.new(); var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR; env.background_color=Color("29343c")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color=Color("d8e3ef"); env.ambient_light_energy=0.9
	environment.environment=env; scene.add_child(environment)
	var sun:=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-48,-32,0); sun.light_energy=1.6; scene.add_child(sun)
	var actor:=Node3D.new(); actor.set_script(load("res://scripts/player_3d.gd")); scene.add_child(actor)
	var animation:=actor.model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	animation.seek(0.30,true); actor.tick(0.0)
	await process_frame; await process_frame
	var hand: Vector3=actor.skeleton.to_global(actor.skeleton.get_bone_global_pose(actor.right_hand).origin)
	print("HAND ",hand," WEAPON ",actor.weapon_model.global_position," MUZZLE ",actor.muzzle_position())
	for bone_name in ["hand_l","middle_01_r","middle_02_r","index_01_r","index_02_r"]:
		var bone_id: int=actor.skeleton.find_bone(bone_name)
		var pose: Transform3D=actor.skeleton.get_bone_global_pose(bone_id)
		print(bone_name," ",actor.skeleton.to_global(pose.origin)," AXES ",actor.skeleton.to_global(pose.origin+pose.basis.x)-actor.skeleton.to_global(pose.origin)," / ",actor.skeleton.to_global(pose.origin+pose.basis.y)-actor.skeleton.to_global(pose.origin)," / ",actor.skeleton.to_global(pose.origin+pose.basis.z)-actor.skeleton.to_global(pose.origin))
	var camera:=Camera3D.new(); scene.add_child(camera); camera.fov=32; camera.current=true
	for view in ["front","side","back"]:
		match view:
			"front": camera.position=hand+Vector3(0.05,0.16,-1.05)
			"side": camera.position=hand+Vector3(1.05,0.12,-0.08)
			"back": camera.position=hand+Vector3(0.05,0.16,1.05)
		camera.look_at(hand+Vector3(-0.02,0.0,-0.02))
		await create_timer(0.12).timeout; await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://diagnostics/hand_"+view+".png")
	actor.ammo=3; actor.request_reload(); animation.seek(0.4,true); actor.tick(0.0)
	await create_timer(0.20).timeout; await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/hand_reload_closeup.png")
	animation.play("Pistol_Aim_Neutral"); animation.seek(animation.get_animation("Pistol_Aim_Neutral").length,true); actor.tick(0.0)
	await process_frame; await process_frame
	hand=actor.skeleton.to_global(actor.skeleton.get_bone_global_pose(actor.right_hand).origin)
	print("NEUTRAL_HAND ",hand)
	for view in ["front","side","back"]:
		match view:
			"front": camera.position=hand+Vector3(0.05,0.16,-1.05)
			"side": camera.position=hand+Vector3(1.05,0.12,-0.08)
			"back": camera.position=hand+Vector3(0.05,0.16,1.05)
		camera.look_at(hand+Vector3(-0.02,0.0,-0.02))
		await create_timer(0.12).timeout; await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://diagnostics/neutral_"+view+".png")
	quit()
