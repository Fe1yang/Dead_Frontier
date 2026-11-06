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
	var roadside:=load("res://scripts/corpse_3d.gd").new() as Node3D
	roadside.seed_value=4401
	roadside.position=Vector3(-5.0,0.17,-2.8)
	game.add_child(roadside)
	assert(roadside.bodies.size()==1)
	var pile: Node3D=game._spawn_obstacle("corpse_pile",-1.55,-5.0)
	assert(pile.half_extents.is_equal_approx(Vector2(0.92,1.16)))
	assert(pile.damage==9.0)
	assert(pile.overlaps(Vector3(-1.55,0,-5.0)))
	assert(not pile.overlaps(Vector3(1.0,0,-5.0)))
	var car: Node3D=game._spawn_obstacle("car",1.55,-9.5,false,2)
	assert(car.half_extents.is_equal_approx(Vector2(1.02,2.08)))
	game.camera.position=Vector3(0,5.4,9.2)
	game.camera.fov=50
	game.camera.look_at(Vector3(-0.5,0.30,-4.6))
	await create_timer(0.30).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/dead-frontier-corpses.png")==OK)
	print("CORPSES_CAPTURED")
	game._spawn_obstacle("car",-2.4,-20.0,false,0)
	game._spawn_obstacle("corpse_pile",0.0,-20.0)
	assert(not game._route_remains_open("car",2.4,-20.0))
	print("CORPSE_ROUTE_GUARD_PASS")
	# Early-run patterns never contain two obstacles, even with a fixed deterministic seed.
	game.distance=100.0
	for i in range(80):
		for obstacle in game.obstacles:
			obstacle.free()
		game.obstacles.clear()
		game._spawn_obstacle_pattern()
		assert(game.obstacles.size()<=1)
	print("EARLY_RUN_SINGLE_OBSTACLE_PASS")
	print("CORPSE_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
