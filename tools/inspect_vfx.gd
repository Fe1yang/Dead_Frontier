extends SceneTree

var scene: Node3D
var camera: Camera3D

func _initialize() -> void:
	call_deferred("inspect")

func inspect() -> void:
	root.size=Vector2i(960,720)
	scene=Node3D.new(); root.add_child(scene)
	var environment:=WorldEnvironment.new(); var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR; env.background_color=Color("36424a")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color=Color("d7e0e8"); env.ambient_light_energy=0.75
	environment.environment=env; scene.add_child(environment)
	var sun:=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-48,-32,0); sun.light_energy=1.0; scene.add_child(sun)
	var ground:=MeshInstance3D.new(); var plane:=PlaneMesh.new(); plane.size=Vector2(200,200)
	ground.mesh=plane; var mat:=StandardMaterial3D.new(); mat.albedo_color=Color("41484a"); ground.material_override=mat; scene.add_child(ground)
	var barrel:=load("res://assets/models/barrel.glb").instantiate() as Node3D
	barrel.scale=Vector3.ONE*1.35; barrel.position=Vector3(-1.8,0,0); scene.add_child(barrel)
	camera=Camera3D.new(); scene.add_child(camera); camera.position=Vector3(3.4,3.4,6.5); camera.look_at(Vector3(-0.25,1.0,0)); camera.fov=48; camera.current=true
	await process_frame
	var variant: String="air" if "--air" in OS.get_cmdline_user_args() else "ground"
	var fx:=load("res://assets/BinbunVFX_Vol2/ExplosionFX/effects/"+variant+"/vfx_"+variant+"_explosion_01.tscn").instantiate() as Node3D
	fx.set("one_shot",true); fx.set("autoplay",false); fx.set("audio_stream",null); fx.set("emission",1.15); fx.set("light_energy",1.4)
	fx.scale=Vector3.ONE*0.85; scene.add_child(fx)
	if "--plain" in OS.get_cmdline_user_args():
		ground.position.y=-2.0
		var plain:=StandardMaterial3D.new(); plain.albedo_color=Color("ff6a18"); plain.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		fx.get_node("Core").material_override=plain
	var animation:=fx.get_node("AnimationPlayer") as AnimationPlayer
	fx.call("play")
	for child in fx.get_children():
		if child is GPUParticles3D:
			child.local_coords=true
			child.visibility_aabb=AABB(Vector3(-20,-20,-20),Vector3(40,40,40))
			child.restart()
			var process:=child.process_material as ParticleProcessMaterial
			print("PARTICLE ",child.name," emitting=",child.emitting," local=",child.local_coords," scale=",process.scale_min,"/",process.scale_max," offset=",process.emission_shape_offset," mesh=",child.draw_pass_1)
	print("VFX_PLAY ",variant," ",animation.current_animation," at ",animation.current_animation_position)
	var elapsed:=0.0
	for mark in [0.02,0.05,0.15,0.35,0.70]:
		await create_timer(float(mark)-elapsed).timeout; elapsed=float(mark)
		await RenderingServer.frame_post_draw
		print("VFX_FRAME ",mark," animation ",animation.current_animation_position," core_emitting=",fx.get_node("Core").emitting)
		root.get_texture().get_image().save_png("res://diagnostics/explosion_"+variant+"_"+str(mark)+".png")
	fx.queue_free(); await process_frame
	quit()
