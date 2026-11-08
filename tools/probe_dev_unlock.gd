extends SceneTree
## Does the dev unlock actually mark everything as owned?

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var game: Node3D = (load("res://scenes/main.tscn") as PackedScene).instantiate() as Node3D
	root.add_child(game)
	await process_frame
	await create_timer(0.4).timeout
	game.call("enter_lobby")
	await process_frame
	var so: Dictionary = game.get("store_owned")
	print("STORE_OWNED ", so.size())
	for id in ["vehicle_bike","vehicle_sport","vehicle_car","vehicle_gold","vehicle_tank"]:
		print("OWNED ", id, "=", game.call("vehicle_is_owned", id))
	print("CHARS ", game.get("owned_characters"), " PETS ", game.get("owned_pets"), " SKINS ", game.get("owned_skins"))
	print("DEV_UNLOCK_PROBE_DONE")
	game.queue_free()
	await process_frame
	quit()
