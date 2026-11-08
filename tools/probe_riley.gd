extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/riley_%s.png" % n)
	print("SHOT ", n)
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.set("character_choice", 1)
	main.call("enter_lobby")
	await create_timer(0.8).timeout
	await _shot("1_lobby")
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.6).timeout
	var p = main.get("player")
	print("PLAYER asset=", p.get("asset_path") if p.get("asset_path")!=null else "?", " clips=", (p.get("animation_player") as AnimationPlayer).get_animation_list() if p.get("animation_player") else [])
	await _shot("2_run")
	print("RILEY_DONE")
	quit()
