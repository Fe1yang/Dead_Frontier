extends SceneTree

func _initialize() -> void:
	call_deferred("inspect")

func inspect() -> void:
	root.size=Vector2i(1000,750)
	var scene:=Node3D.new()
	root.add_child(scene)
	var environment:=WorldEnvironment.new()
	var env:=Environment.new()
	env.background_mode=Environment.BG_COLOR
	env.background_color=Color("29343c")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color("d8e3ef")
	env.ambient_light_energy=0.75
	environment.environment=env
	scene.add_child(environment)
	var sun:=DirectionalLight3D.new()
	sun.rotation_degrees=Vector3(-48,-32,0)
	sun.light_energy=1.8
	sun.shadow_enabled=true
	scene.add_child(sun)
	var floor:=MeshInstance3D.new()
	var plane:=PlaneMesh.new()
	plane.size=Vector2(12,12)
	floor.mesh=plane
	var mat:=StandardMaterial3D.new()
	mat.albedo_color=Color("39454a")
	floor.material_override=mat
	scene.add_child(floor)
	var actor:=Node3D.new()
	actor.set_script(load("res://scripts/player_3d.gd"))
	scene.add_child(actor)
	var camera:=Camera3D.new()
	scene.add_child(camera)
	camera.position=Vector3(3.4,2.1,2.8)
	camera.look_at(Vector3(0,1.25,0.30),Vector3.UP)
	camera.fov=42
	camera.current=true
	for weapon_id in ["PISTOL","SMG","SHOTGUN","SNIPER"]:
		actor.set_weapon(weapon_id)
		await create_timer(0.18).timeout
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://diagnostics/weapons_hd/side_"+weapon_id.to_lower()+".png")
	print("WEAPON_SIDE_CAPTURES_SAVED")
	quit()
