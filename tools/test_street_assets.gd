extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _capture(game: Node3D,label: String) -> void:
	game.damage_flash=0.0
	await create_timer(0.20).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/street-enriched/"+label+".png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("STREET_CAPTURE ",path)

func _run() -> void:
	print("STREET_TEST_BEGIN")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/street-enriched"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	print("STREET_GAME_ADDED roads=",game.roads.size())
	await process_frame
	game.set_process(false)
	game.state="playing"; game.player.visible=true; game.set_weather("clear"); game.distance=0.0; game._apply_day_night()
	game.camera.position=Vector3(0,6.4,13.5); game.camera.fov=52; game.camera.h_offset=0; game.camera.v_offset=0
	game.camera.look_at(Vector3(0,1,-8))
	print("STREET_FULL_CITY_VISIBLE")
	var police: Node3D=game._spawn_obstacle("police",0.0,-3.8)
	assert(police.kind=="police")
	assert(police.half_extents.is_equal_approx(Vector2(1.08,2.42)))
	assert(police.overlaps(Vector3(0,0,-3.8)))
	assert(not police.overlaps(Vector3(3.0,0,-3.8)))
	assert(police.model.get_child_count()>0)
	assert(is_instance_valid(police.police_red) and is_instance_valid(police.police_blue))
	var red_before: float=police.police_red.light_energy
	var blue_before: float=police.police_blue.light_energy
	police._tick_police_lights(0.25)
	assert(police.police_red.light_energy!=red_before and police.police_blue.light_energy!=blue_before)
	print("STREET_POLICE_LIGHT_AND_COLLISION_ASSERTIONS_PASS")
	await _capture(game,"district-02-police")
	police.position.z=-7.5
	await _capture(game,"district-02-clear")
	police.visible=false
	var crosswise: Node3D=game._spawn_obstacle("police",-0.85,-4.8,true)
	assert(crosswise.police_crosswise)
	assert(crosswise.half_extents.is_equal_approx(Vector2(2.42,1.08)))
	assert(crosswise.overlaps(Vector3(-2.8,0,-4.8)))
	assert(not crosswise.overlaps(Vector3(2.65,0,-4.8)))
	var shoulder_wreck: Node3D=game._spawn_obstacle("car",3.18,-11.5)
	assert(shoulder_wreck.kind=="car" and shoulder_wreck.damage==22.0)
	assert(shoulder_wreck.position.x+shoulder_wreck.half_extents.x>4.19)
	await _capture(game,"police-crosswise-and-wreck")
	print("STREET_CROSSWISE_AND_SHOULDER_ASSERTIONS_PASS")
	crosswise.position.z=-20.0; shoulder_wreck.position.z=-20.0
	game.distance=10000.0; game._apply_day_night()
	await _capture(game,"district-02-night")
	game.distance=0.0; game._apply_day_night()
	for i in range(game.roads.size()): game.roads[i].position.z=(6-i)*16.0
	await _capture(game,"district-06-bus-clear")
	for i in range(game.roads.size()): game.roads[i].position.z=(2-i)*16.0
	game.hud.visible=false
	game.camera.position=Vector3(0,4.0,4.0); game.camera.look_at(Vector3(7.95,3.0,-4.0))
	await _capture(game,"window-recess-detail")
	game.hud.visible=true
	game.camera.position=Vector3(0,6.4,13.5); game.camera.look_at(Vector3(0,1,-8))
	police.visible=true; police.position.z=-3.8
	var health_before: float=game.player.health
	game.player.position=Vector3(0,0,-3.8); game.player.target_x=0.0
	police.hit_cooldown=0.0
	game._tick_obstacles(0.0)
	assert(game.player.health<health_before)
	assert(not police.overlaps(game.player.position))
	print("STREET_POLICE_COLLISION_PASS health=",game.player.health," player_x=",game.player.position.x)
	print("STREET_ASSETS_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
