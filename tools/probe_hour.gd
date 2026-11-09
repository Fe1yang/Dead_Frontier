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
	var counts := {"clear":0, "dusk":0, "dawn":0, "rain":0, "fog":0, "storm":0}
	for trial in 30:
		main.set("runs_this_launch", 2)          # not the first run
		main.call("enter_lobby")
		await create_timer(0.05).timeout
		main.set("loadout_on", false); main.set("owned_vehicle", "")
		main.call("start_run", true, true)
		await create_timer(0.05).timeout
		var w := String(main.get("weather"))
		counts[w] = int(counts.get(w, 0)) + 1
		if String(main.get("state")) == "intro":
			main.call("_finish_intro")
	print("HOUR_SAMPLE ", counts)
	print("HOUR_DONE")
	quit()
