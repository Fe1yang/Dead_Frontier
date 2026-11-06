extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _capture(label: String) -> void:
	await create_timer(0.12).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/coin/"+label+".png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("COIN_CAPTURE ",path)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/coin"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.set_process(false); game.set_physics_process(false); game._clear_world(); game.state="playing"; game.set_weather("clear"); game.hud.visible=false
	game._spawn_zombie(-4.0,"walker")
	var zombie: Node3D=game.zombies[0]; zombie.position=Vector3(0,0,-4.0)
	var balance_before: int=game.run_coins
	game._hit_zombie(zombie,10000.0)
	for step in range(6): game._tick_blood(0.08)
	assert(game.blood_pools.size()>=2)
	assert(game.pickups.size()==1)
	var coin: Node3D=game.pickups[0]
	assert(coin.kind=="coin" and coin.value>0 and coin.source_kind=="walker")
	assert(coin.coin_pieces.size()==7)
	assert(game.run_coins==balance_before)
	game.player.position=Vector3(0,0,3.0); game.player.target_x=0.0
	game._tick_pickups(0.0)
	assert(game.run_coins==balance_before and game.pickups.has(coin))
	print("COIN_NO_CONTACT_NO_CREDIT_PASS")
	game.camera.position=Vector3(1.25,1.65,0.2); game.camera.look_at(Vector3(0,0.12,-4.0))
	game._tick_pickups(0.10)
	await _capture("coin-drop-scattering")
	for step in range(6): game._tick_pickups(0.10)
	assert(is_instance_valid(coin) and coin.scatter_elapsed>=0.48)
	game.camera.position=coin.position+Vector3(1.25,1.65,4.2)
	game.camera.look_at(coin.position+Vector3(0,0.12,0))
	await _capture("coin-drop-settled")
	var value: int=coin.value
	game.player.position=coin.position; game.player.target_x=coin.position.x
	game._tick_pickups(0.0)
	assert(game.run_coins==balance_before+value)
	assert(game.pickups.is_empty())
	assert(int(game.kill_coins.get("walker",0))==value)
	print("COIN_CONTACT_PICKUP_PASS value=",value)
	print("COIN_DROP_TEST_PASS scatter_pieces=7 no_remote_credit=true contact_required=true")
	game.queue_free(); await process_frame; quit()
