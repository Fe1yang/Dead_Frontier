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
	main.call("set_lobby_tab", 1)
	await create_timer(0.5).timeout
	print("PETS count=", main.get("lobby").PETS.size())
	main.get("owned_pets").append(5)
	main.set("pet_choice", 5)
	main.set("pet_equipped", true)
	main.call("enter_lobby")
	await create_timer(1.2).timeout
	var lobby = main.get("lobby")
	var pet = lobby.get("pet")
	print("pet node=", pet != null)
	if pet != null:
		var ap: AnimationPlayer = pet.find_child("AnimationPlayer", true, false)
		print("pet clip=", ap.current_animation if ap else "none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/lion_lobby.png")
	print("LION_DONE")
	quit()
