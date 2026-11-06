extends SceneTree
## Quick look at the current road paint: two intersections and one normal block,
## shot from above so every lane line and crossing is visible.

var game: Node3D

func _initialize() -> void:
	call_deferred("_run")

func select_district(index: int) -> void:
	for i in range(game.roads.size()): game.roads[i].position.z=(index-i)*16.0

func capture(label: String) -> void:
	await create_timer(0.16).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/roads/"+label+".png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("ROAD_CAPTURE ",path)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/roads"))
	game=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.set_process(false); game.set_physics_process(false); game.state="playing"; game.set_weather("clear")
	game.hud.visible=false; game.player.visible=false
	for z in game.zombies: z.visible=false
	game.camera.h_offset=0; game.camera.v_offset=0
	# Bird's eye over an intersection district.
	for idx in [5,11,17]:
		select_district(idx)
		game.camera.position=Vector3(0,15.5,9.5); game.camera.fov=50
		game.camera.look_at(Vector3(0,0,-4),Vector3.UP)
		await capture("intersection-%02d-after2"%idx)
	# Street-level view of a normal block's lane lines.
	select_district(3)
	game.camera.position=Vector3(0,4.6,11.0); game.camera.fov=55
	game.camera.look_at(Vector3(0,0.6,-6),Vector3.UP)
	await capture("block-03-after2")
	print("ROAD_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
