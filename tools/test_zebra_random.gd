extends SceneTree
const OUTPUT_DIR: String="C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/diagnostics/zebra"
func _initialize() -> void:
	call_deferred("_run")
func _capture(game: Node3D,variant: int,label: String) -> void:
	for i in range(game.roads.size()): game.roads[i].position.z=(6-i)*16.0
	game.roads[variant].position.z=-2.0
	game.camera.position=Vector3(0,6.2,12.0)
	game.camera.fov=52
	game.camera.look_at(Vector3(0,0,-3.0))
	await create_timer(0.25).timeout
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/"+label+".png")==OK)
	print("ZEBRA_CAPTURE ",variant)
func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	game.set_process(false); game.state="playing"; game.hud.visible=false
	game.set_weather("clear"); game.distance=0.0; game._apply_day_night()
	for v in [2,9,16,23]:
		await _capture(game,v,"intersection-%02d"%v)
	print("ZEBRA_CROSSING_TEST_PASS")
	game.queue_free()
	await process_frame
	quit()
