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
	main.call("start_run", true, true)
	await create_timer(1.5).timeout
	var z = (main.get("zombies") as Array).size()
	var r = (main.get("roads") as Array).size()
	print("smoke: state=", main.get("state"), " zombies=", z, " districts=", r)
	print("SMOKE_DONE")
	quit()
