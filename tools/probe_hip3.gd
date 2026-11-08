extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.8).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	main.call("start_run", true, true)
	await create_timer(0.3).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	for i in range(8):
		main.call("_spawn_zombie", -8.0 - float(i), "walker")
	await create_timer(0.5).timeout
	for q in (main.get("zombies") as Array):
		if not is_instance_valid(q): continue
		var ap: AnimationPlayer = q.get("animation_player")
		var sk: Skeleton3D = q.find_children("*", "Skeleton3D", true, false)[0]
		var bi: int = sk.find_bone("pelvis")
		print("INGAME clip=", ap.current_animation, " pelvis_y=", snappedf(sk.get_bone_global_pose(bi).origin.y, 0.001), " model_y=", snappedf(q.get_node("Model").position.y if q.has_node("Model") else 0.0, 0.001))
	print("HIP3_DONE")
	quit()
