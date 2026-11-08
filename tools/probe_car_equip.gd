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
	print("sedan owned=", main.call("vehicle_is_owned", "vehicle_sedan"), " tank owned=", main.call("vehicle_is_owned", "vehicle_tank"))
	main.call("set_lobby_tab", 3)
	await create_timer(0.3).timeout
	main.call("_lobby_tap", (main.call("lobby_card_rect", 5) as Rect2).get_center())
	await create_timer(0.2).timeout
	print("equipped=", main.get("owned_vehicle"))
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	print("RUN vehicle=", main.get("player").get("vehicle"))
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -6.0, "walker")
	main.call("_spawn_zombie", -8.0, "walker")
	await create_timer(0.4).timeout
	for q in (main.get("zombies") as Array):
		if is_instance_valid(q):
			print("Z clip=", (q.get("animation_player") as AnimationPlayer).current_animation)
	print("EQUIP_DONE")
	quit()
