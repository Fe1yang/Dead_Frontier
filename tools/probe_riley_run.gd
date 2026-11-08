extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.set("character_choice", 1)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.8).timeout
	var p = main.get("player")
	var ap: AnimationPlayer = p.get("animation_player")
	print("run clip=", ap.current_animation if ap else "none", " choice=", main.get("character_choice"))
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/riley_run3.png")
	print("RUN3_DONE")
	quit()
