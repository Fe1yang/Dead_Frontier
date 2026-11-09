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
	var t0 := Time.get_ticks_msec()
	var worst := 0
	var last := t0
	while Time.get_ticks_msec() - t0 < 20000:
		await process_frame
		var now := Time.get_ticks_msec()
		worst = maxi(worst, now - last); last = now
	print("20 s played, worst frame ", worst, " ms, zombies=", (main.get("zombies") as Array).size(),
		" districts=", (main.get("roads") as Array).size(), " state=", main.get("state"))
	print("LR_DONE")
	quit()
