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
	await create_timer(0.6).timeout
	main.call("set_lobby_tab", 1)
	await create_timer(0.4).timeout
	var ls = main.get("lobby")
	for p in ["white_tiger", "lion"]:
		ls.call("show_pet", "res://assets/models/pets/%s.glb" % p)
		await create_timer(0.9).timeout
		var pet = ls.get("pet")
		var ap = pet.find_child("AnimationPlayer", true, false) if pet else null
		print(p, " clip=", ap.current_animation if ap else "none", " playing=", ap.is_playing() if ap else false)
	print("PETA_DONE")
	quit()
