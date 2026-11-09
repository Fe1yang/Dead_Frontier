extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.5).timeout
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -8.0, "jockey")
	await create_timer(0.6).timeout
	for q in (main.get("zombies") as Array):
		if String(q.get("kind")) == "jockey":
			var ap = q.get_node_or_null("AnimationPlayer")
			if ap == null:
				for n in q.find_children("*", "AnimationPlayer", true, false):
					ap = n
					break
			print("jockey clip=", ap.current_animation if ap else "none",
				" speed=", ap.speed_scale if ap else 0.0,
				" anims=", ap.get_animation_list() if ap else [])
	print("JKC_DONE")
	quit()
