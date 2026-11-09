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
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	var zs = main.get("zombies") as Array
	for z in zs:
		if is_instance_valid(z):
			print("SPAWN ", z.kind, " z=", snappedf(z.position.z,0.1), " speed=", snappedf(z.speed,0.1))
	await create_timer(2.5).timeout
	for z in zs:
		if is_instance_valid(z):
			print("LATER ", z.kind, " z=", snappedf(z.position.z,0.1))
	print("OPENING_DONE")
	quit()
