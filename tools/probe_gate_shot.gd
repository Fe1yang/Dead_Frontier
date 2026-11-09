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
	await create_timer(0.4).timeout
	main.set("character_choice", 0)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(0.4).timeout
	main.get("player").call("set_weapon", "RIFLE")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9); main.set("gate_timer", 1.0e9)
	main.call("_spawn_gate")
	await create_timer(0.5).timeout
	var gates = main.get("gates")
	print("gates=", gates.size() if gates != null else "null")
	if gates != null and gates.size() > 0:
		var g = gates[0]
		print("gate pos=", g.position)
		# park the gate close in front of Mason
		g.position = Vector3(0, g.position.y, -7.0)
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/shot_gate.png")
	print("GATE_SHOT_DONE")
	quit()
