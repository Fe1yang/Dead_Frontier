extends SceneTree
## Capture clean vehicle preview (bike front) for lobby card thumbnail.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/bike"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	await create_timer(0.6).timeout
	game._clear_world(); game.enter_lobby()
	await create_timer(0.5).timeout
	game.set_lobby_tab(3)
	await create_timer(0.8).timeout; await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png("res://diagnostics/bike/bike_front.png")==OK)
	print("BIKE_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
