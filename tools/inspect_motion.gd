extends SceneTree

var scene: Node3D
var camera: Camera3D

func _initialize() -> void:
	call_deferred("inspect")

func setup_scene() -> void:
	root.size=Vector2i(1000,750)
	scene=Node3D.new(); root.add_child(scene)
	var environment:=WorldEnvironment.new(); var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR; env.background_color=Color("29343c")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color=Color("d8e3ef"); env.ambient_light_energy=0.8
	environment.environment=env; scene.add_child(environment)
	var sun:=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-48,-32,0); sun.light_energy=1.7; scene.add_child(sun)
	camera=Camera3D.new(); scene.add_child(camera); camera.position=Vector3(3.4,2.0,3.1); camera.look_at(Vector3(0,1.0,0)); camera.fov=42; camera.current=true

func frame(name: String) -> void:
	await create_timer(0.22).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/"+name+".png")

func inspect() -> void:
	setup_scene()
	var actor:=Node3D.new(); actor.set_script(load("res://scripts/player_3d.gd")); scene.add_child(actor)
	var animation:=actor.model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	print("PLAYER_ANIMATIONS ",animation.get_animation_list())
	for i in range(3): actor.tick(0.0); await frame("motion_player_"+str(i))
	actor.ammo=3; actor.request_reload()
	for i in range(3): actor.tick(0.0); await frame("motion_reload_"+str(i))
	actor.queue_free(); await process_frame
	var zombie:=Node3D.new(); zombie.set_script(load("res://scripts/zombie_3d.gd")); scene.add_child(zombie); zombie.configure("walker",1.0)
	animation=zombie.model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	print("ZOMBIE_ANIMATIONS ",animation.get_animation_list()," current=",animation.current_animation)
	for i in range(4): await frame("motion_zombie_"+str(i))
	print("MOTION_CAPTURES_SAVED")
	quit()
