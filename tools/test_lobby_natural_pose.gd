extends SceneTree
const OUTPUT_DIR: String="C:/Users/user/Documents/kimi/tasks/2026-11-04/00-09-49-288c0219/diagnostics"
func _initialize() -> void:
	call_deferred("_run")
func _capture(game: Node3D,label: String) -> void:
	game.camera.position=game.lobby.camera_position()
	game.camera.fov=38.0
	game.camera.look_at(game.lobby.camera_target())
	await create_timer(0.25).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/"+label+".png")==OK)
func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game.state="lobby"
	game.hud.visible=false
	game.lobby.visible=true
	for i in range(3):
		game.lobby.show_character(i)
		assert(game.lobby.actor.find_child("BlinkLids",true,false)==null)
		await _capture(game,"lobby-natural-%d-front"%i)
		game.lobby.actor.rotation.y=PI
		await _capture(game,"lobby-natural-%d-back"%i)
		game.lobby.spin=0.0; game.lobby.spin_velocity=0.0; game.lobby.actor.rotation.y=0.0
	print("LOBBY_NATURAL_POSE_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
