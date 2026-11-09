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
	main.set("pet_choice", 2)
	main.set("pet_equipped", true)
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	var pets: Array = main.get("companion_pets")
	print("pets spawned: ", pets.size())
	for d in pets:
		var anim = d.get("anim")
		if anim == null:
			print("  no anim player")
			continue
		print("  clip=", anim.current_animation, " playing=", anim.is_playing(), " has Dog_Run=", anim.has_animation("Dog_Run"))
	print("PC_DONE")
	quit()
