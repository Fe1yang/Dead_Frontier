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
	await create_timer(0.5).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(1.0).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(6.0).timeout
	var total := 0.0
	var worst := 0.0
	var n := 240
	var prev := Time.get_ticks_usec()
	for i in range(n):
		await process_frame
		var now := Time.get_ticks_usec()
		var ms := float(now - prev) / 1000.0
		prev = now
		total += ms
		if ms > worst: worst = ms
	var avg := total / float(n)
	print("FRAME avg=%0.2f ms worst=%0.2f ms fps=%0.0f" % [avg, worst, 1000.0 / avg])
	var meshes := 0
	for m in main.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.is_visible_in_tree(): meshes += 1
	var parts := 0
	for p in main.find_children("*", "CPUParticles3D", true, false):
		var cp := p as CPUParticles3D
		if cp.emitting and cp.is_visible_in_tree(): parts += 1
	print("VISIBLE meshes=", meshes, " particles=", parts, " zombies=", (main.get("zombies") as Array).size())
	print("PERF_DONE")
	quit()
