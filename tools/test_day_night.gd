extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/day-night"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game.state="playing"; game.player.visible=true; game.set_weather("clear")
	game.camera.position=Vector3(0,6.4,13.5); game.camera.fov=52; game.camera.h_offset=0; game.camera.v_offset=0
	game.camera.look_at(Vector3(0,1,-8))
	for i in range(game.zombies.size()):
		game.zombies[i].position=Vector3((i-1)*1.8,0,-3.0-i*4.0)
	for metres in [0.0,5000.0,10000.0,15000.0,20000.0]:
		game.player.position=Vector3(0,0,4.5); game.player.target_x=0.0; game.player.set_aim(Vector3.FORWARD)
		game.player.force_update_transform(); game.player.tick(0.0)
		game.distance=metres; game._apply_day_night()
		if is_equal_approx(metres,0.0) or is_equal_approx(metres,20000.0): assert(game.night_amount<0.001)
		if is_equal_approx(metres,10000.0):
			assert(game.night_amount>0.999)
			assert(game.player.torch.visible and game.player.torch.light_energy>8.9)
			print("TORCH_DEBUG player=",game.player.global_position," local=",game.player.torch.position," pos=",game.player.torch.global_position," forward=",-game.player.torch.global_basis.z," muzzle=",game.player.muzzle_position()," energy=",game.player.torch.light_energy)
		if is_equal_approx(metres,5000.0) or is_equal_approx(metres,15000.0): assert(absf(game.night_amount-0.5)<0.001)
		await create_timer(0.20).timeout; await RenderingServer.frame_post_draw
		var label: String=str(int(metres))
		assert(root.get_texture().get_image().save_png("res://diagnostics/day-night/"+label+"m.png")==OK)
		print("DAY_NIGHT_SAMPLE metres=",metres," night=",game.night_amount," sun_energy=",game.sun_light.light_energy)
	print("DAY_NIGHT_TEST_PASS day=0m dusk=5000m night=10000m dawn=15000m day=20000m")
	quit()
