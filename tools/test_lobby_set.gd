extends SceneTree
## Lobby wide shot to review the refined background set and the dimmed lantern.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/lobby"))
	var game: Node3D=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.go_to_lobby(); await create_timer(0.5).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/lobby/set-refined.png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("SET_CAPTURE ",path)
	game.queue_free(); await process_frame; quit()
