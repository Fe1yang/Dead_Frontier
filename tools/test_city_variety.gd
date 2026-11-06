extends SceneTree

var game: Node3D

func _initialize() -> void:
	call_deferred("_run")

func select_district(index: int) -> void:
	for i in range(game.roads.size()): game.roads[i].position.z=(index-i)*16.0

func capture(label: String) -> void:
	await create_timer(0.16).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/city-variety/"+label+".png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("CITY_VARIETY_CAPTURE ",path)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/city-variety"))
	game=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	assert(game.roads.size()==24)
	game.set_process(false); game.set_physics_process(false); game.state="playing"; game.set_weather("clear")
	game.hud.visible=false; game.player.visible=false
	for z in game.zombies: z.visible=false
	game.camera.h_offset=0; game.camera.v_offset=0
	select_district(0)
	game.camera.position=Vector3(0,5.6,12.5); game.camera.fov=58; game.camera.look_at(Vector3(0,3,-5))
	await capture("district-00-low-rise")
	select_district(1)
	game.camera.position=Vector3(0,4.2,9.0); game.camera.fov=58; game.camera.look_at(Vector3(0,1,-4))
	await capture("district-01-pine-and-flowerbed")
	select_district(15)
	game.camera.position=Vector3(0,3.0,3.8); game.camera.fov=52; game.camera.look_at(Vector3(5.5,.1,-1.15))
	await capture("district-15-pavement-patch")
	select_district(14)
	game.camera.position=Vector3(1.8,5.4,7.4); game.camera.fov=58; game.camera.look_at(Vector3(-.65,-.25,.25))
	await capture("district-14-missile-crater")
	select_district(6)
	game.camera.position=Vector3(0,7.4,14.0); game.camera.fov=60; game.camera.look_at(Vector3(0,7.5,-6))
	await capture("district-06-high-rise")
	select_district(18)
	game.camera.position=Vector3(0,7.4,14.0); game.camera.fov=60; game.camera.look_at(Vector3(0,7.5,-6))
	await capture("district-18-tower-center")
	print("CITY_VARIETY_CAPTURE_PASS districts=24")
	game.queue_free(); await process_frame; quit()
