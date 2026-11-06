extends SceneTree
## Health-strip checks: 3 cells at 100 HP, a half cell at +50%, a quarter cell at +25%,
## and a second stacked row when the meter grows past four rectangles.

var game: Node3D

func _initialize() -> void:
	call_deferred("_run")

func _snap(maxhp: float,hp: float,label: String) -> void:
	game.player.max_health=maxhp; game.player.health=hp
	game.hud.queue_redraw()
	await create_timer(0.16).timeout; await RenderingServer.frame_post_draw
	var img:=root.get_texture().get_image().get_region(Rect2i(0,0,300,120))
	var path:="res://diagnostics/hud/health-"+label+".png"
	assert(img.save_png(path)==OK)
	print("HEALTH_CAPTURE ",path)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/hud"))
	game=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.set_process(false); game.set_physics_process(false); game.state="playing"; game.set_weather("clear")
	game.player.visible=false
	for z in game.zombies: z.visible=false
	await _snap(100.0,100.0,"default-3")
	await _snap(150.0,150.0,"plus-half")
	await _snap(125.0,125.0,"plus-quarter")
	await _snap(241.7,241.7,"two-rows")
	print("HEALTH_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
