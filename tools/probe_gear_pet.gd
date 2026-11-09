extends SceneTree
var main: Node

func _initialize() -> void:
	call_deferred("_run")

func _lamp(at: Vector3) -> void:
	var l := OmniLight3D.new()
	l.light_energy = 5.0
	l.omni_range = 8.0
	l.shadow_enabled = false
	main.add_child(l)
	l.global_position = at

func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.0).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	await create_timer(0.6).timeout

	var p = main.get("player")
	p.call("set_armor", true)
	p.call("set_helmet", true)
	await create_timer(0.4).timeout

	var pos: Vector3 = p.global_position
	_lamp(Vector3(pos.x, pos.y + 2.2, pos.z + 1.8))
	_lamp(Vector3(pos.x - 1.6, pos.y + 1.6, pos.z - 0.8))
	await create_timer(0.3).timeout

	# gear: three-quarter front, chest height, 2.4 m back
	main.call("debug_camera_at", Vector3(pos.x - 1.7, pos.y + 1.5, pos.z + 1.8),
		Vector3(pos.x, pos.y + 1.25, pos.z), 34.0)
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/shot_gear.png")
	print("gear shot done")

	# pet: recruit the wolfdog and shoot it side-on
	main.call("_recruit_pet", 2, Vector3(pos.x + 1.8, 0.0, pos.z - 3.2))
	await create_timer(1.2).timeout
	var pets: Array = main.get("companion_pets")
	var target: Vector3 = Vector3(pos.x + 1.8, 0.0, pos.z - 3.2)
	if pets.size() > 0:
		target = (pets[0] as Node3D).global_position
	print("pet at ", target)
	_lamp(Vector3(target.x, 1.6, target.z + 1.4))
	await create_timer(0.3).timeout
	main.call("debug_camera_at", Vector3(target.x - 2.6, 1.1, target.z + 1.2),
		Vector3(target.x, 0.5, target.z), 40.0)
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/shot_pet.png")
	print("pet shot done")
	print("SHOTS_DONE")
	quit()
