extends SceneTree
## Screenshot the developer letter: mail list, then the opened letter with its gift line.

var game: Node3D

func _initialize() -> void:
	call_deferred("_run")

func capture(label: String) -> void:
	await create_timer(0.2).timeout
	await RenderingServer.frame_post_draw
	var path: String="res://diagnostics/mail/"+label+".png"
	assert(root.get_texture().get_image().save_png(path)==OK)
	print("MAIL_CAPTURE ",path)

func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://diagnostics/mail"))
	game=(load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game); await process_frame
	game.language_code="zh_CN"
	game.mail_claimed={}
	game.open_mail()
	await capture("letter-list")
	game.open_letter(0)
	await capture("letter-open")
	# scroll to the bottom: gift line and claim button
	game.mail_scroll=game.letter_max_scroll()
	await capture("letter-gift")
	print("MAIL_CAPTURE_PASS")
	game.queue_free(); await process_frame; quit()
