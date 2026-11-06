extends SceneTree

const OUTPUT_DIR: String="C:/Users/user/Documents/kimi/tasks/2026-11-04/00-09-49-288c0219/diagnostics"

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game.state="playing"
	game.player.visible=true
	game.hud.visible=false
	game.set_weather("clear")
	game.distance=0.0
	game._apply_day_night()
	var cars: Array=[]
	var positions: Array=[Vector3(-1.55,0,-2.0),Vector3(1.55,0,-3.0),Vector3(-1.55,0,-8.0),Vector3(1.55,0,-9.0)]
	for tier in range(4):
		var car: Node3D=game._spawn_obstacle("car",positions[tier].x,positions[tier].z,false,tier)
		assert(car.damage_tier==tier)
		assert(car.half_extents.is_equal_approx(Vector2(1.02,2.08)))
		assert(car.damage==22.0)
		cars.append(car)
	game.camera.position=Vector3(0,6.4,9.0)
	game.camera.fov=52
	game.camera.look_at(Vector3(0,0.65,-5.2))
	await create_timer(0.30).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/dead-frontier-damaged-vehicles.png")==OK)
	print("DAMAGED_VEHICLES_CAPTURED")
	# Prove that adding any third full-width vehicle would seal this road section.
	for car in cars: car.visible=false
	game._spawn_obstacle("car",-2.4,-20.0,false,0)
	game._spawn_obstacle("car",0.0,-20.0,false,1)
	assert(not game._route_remains_open("car",2.4,-20.0))
	assert(not game._route_remains_open("police",2.4,-20.0))
	assert(game._route_remains_open("fence",2.4,-20.0)==false)
	print("DAMAGED_VEHICLES_ROUTE_GUARD_PASS")
	print("DAMAGED_VEHICLES_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
