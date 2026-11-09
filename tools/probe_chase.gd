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
	await create_timer(0.3).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.4).timeout
	main.set("spawn_timer", 1.0e9)
	main.call("_chase_begin")
	await create_timer(1.0).timeout
	print("chase_active=", main.get("chase_active"), " gap=", snappedf(float(main.get("chase_gap")),0.1))
	var ch = main.get("chaser")
	print("chaser=", ch != null, " pos=", ch.position if ch != null else Vector3.ZERO)
	if ch != null:
		var ap: AnimationPlayer = ch.find_child("AnimationPlayer", true, false)
		print("chaser clip=", ap.current_animation if ap else "none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/chase_check.png")
	print("CHASE_DONE")
	quit()
