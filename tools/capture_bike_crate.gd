extends SceneTree

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	var game := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(game)
	await process_frame
	game.character_choice=0
	game.player.set_character(0)
	game.start_run(true)
	game._begin_intro()
	game.shot_timer=999
	game.hint_time=0
	game.touch_controls=false
	game._finish_intro()
	var crate: Node3D = game.WeaponCrateScript.new()
	crate.setup("BIKE",5)
	crate.position=Vector3(-1.5,0,game.player.position.z-6)
	game.add_child(crate)
	game.crates.append(crate)
	game.set_process(false)
	for index in range(4):
		crate.weapon_pivot.rotation.y=index*PI*0.5
		await process_frame
		await RenderingServer.frame_post_draw
		var path := "res://diagnostics/medic/crate-bike-%d.png"%index
		assert(game.get_viewport().get_texture().get_image().save_png(path)==OK)
		print("CAPTURE_BIKE_CRATE_SAVED ",path)
	quit()
