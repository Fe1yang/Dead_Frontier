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
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	var p = main.get("player")
	p.call("set_weapon", "FLAME")
	await create_timer(0.3).timeout
	for d in [1.0, 3.0, 6.0, 10.0]:
		var f: float = main.call("_flame_falloff", d)
		print("dist %.0f m -> %.2f x damage  (%.1f dmg/tick)" % [d, f, 22.0 * f])
	print("FF_DONE")
	quit()
