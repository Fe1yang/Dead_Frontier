extends SceneTree
## Top-down paint-layout audit: one overhead shot per district variant.
const OUTPUT_DIR: String="C:/Users/user/Documents/kimi/tasks/2026-11-02/20-32-30-26dbcd78/diagnostics/dashes"
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUTPUT_DIR)
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.set_process(false); game.state="playing"; game.hud.visible=false
	game.set_weather("clear"); game.distance=0.0; game._apply_day_night()
	for r in game.roads:
		var zn:=r.find_child("CITY_zebra_paint",true,false) as Node3D
		if zn: zn.visible=false
	for v in [4,5,11,23]:
		for i in range(game.roads.size()): game.roads[i].position.z=(6-i)*16.0
		game.roads[v].position.z=0.0
		game.camera.position=Vector3(0,26.0,0.01)
		game.camera.fov=30
		game.camera.look_at(Vector3(0,0,0))
		await create_timer(0.2).timeout
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(OUTPUT_DIR+"/block-%02d.png"%v)==OK)
		print("DASH_CAPTURE ",v)
	print("DASH_AUDIT_PASS")
	game.queue_free(); await process_frame; quit()
