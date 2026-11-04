extends Node3D

const ToonStyle=preload("res://scripts/toon_style.gd")

func _ready() -> void:
	get_window().size=Vector2i(1200,800)
	var we:=WorldEnvironment.new(); var env:=Environment.new(); var sky:=Sky.new(); var sky_mat:=PanoramaSkyMaterial.new()
	sky_mat.panorama=load("res://assets/sky/day_cloudy.hdr"); sky_mat.energy_multiplier=1.05; sky.sky_material=sky_mat
	env.background_mode=Environment.BG_SKY; env.sky=sky; env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color=Color("c2c8c7"); env.ambient_light_energy=0.7; env.tonemap_mode=Environment.TONE_MAPPER_ACES; env.tonemap_exposure=1.0
	we.environment=env; add_child(we)
	var sun:=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-42,-28,0); sun.light_energy=1.0; add_child(sun)
	var assets=["survivor","survivor_female","zombie_walker"]
	for i in range(3):
		var model:=load("res://assets/models/"+assets[i]+".glb").instantiate() as Node3D
		model.position=Vector3((i-1)*1.45,0,0); model.rotation.y=0; add_child(model); ToonStyle.apply(model,0.012)
	var ground:=MeshInstance3D.new(); var plane:=PlaneMesh.new(); plane.size=Vector2(12,8); ground.mesh=plane
	var mat:=StandardMaterial3D.new(); mat.albedo_color=Color("454a4c"); ground.material_override=mat; add_child(ground)
	var camera:=Camera3D.new(); camera.projection=Camera3D.PROJECTION_ORTHOGONAL; camera.size=4.1; camera.position=Vector3(3.1,2.45,6.5); add_child(camera)
	camera.current=true; camera.look_at(Vector3(0,1.05,0))
	await get_tree().create_timer(1.0).timeout; await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://renders/comic-lineup-godot.png")
	print("COMIC_LINEUP_SAVED")
	get_tree().quit()
