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
	var owned = main.get("owned_pets")
	owned[4] = true; owned[5] = true
	main.set("pet_equipped", true)
	main.set("pet_choice", 5)          # lion
	main.call("enter_lobby")
	await create_timer(0.6).timeout
	main.set("pet_choice", 4)          # white tiger
	main.call("enter_lobby")
	await create_timer(0.8).timeout
	var lobby = main.get("lobby")
	var pets := []
	for n in lobby.get_children():
		if n.name.begins_with("Dog") or n.name.begins_with("Pet") or n.name.contains("dog") or n.name.contains("lion") or n.name.contains("tiger"):
			pets.append(n.name)
	print("PET_NODES ", pets, " current pet=", lobby.get("pet") != null)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/petswap.png")
	print("PETS_SWAP_DONE")
	quit()
