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
	main.call("_begin_loading", "run")
	var frames := 0
	while String(main.get("state")) == "loading" and frames < 400:
		await process_frame
		frames += 1
	var road = (main.get("roads") as Array)[3]
	var pav := []
	var wall := []
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		var nm := String(mi.name).to_lower()
		var a: AABB = mi.global_transform * mi.get_aabb()
		if nm.find("pavement") != -1:
			pav.append([snappedf(a.position.x,0.01), snappedf(a.end.x,0.01), snappedf(a.position.y,0.01), snappedf(a.end.y,0.01)])
		elif nm.find("wall") != -1 or nm.find("realwall") != -1:
			wall.append([snappedf(a.position.x,0.01), snappedf(a.end.x,0.01)])
	print("pavement pieces=", pav.size())
	for v in pav.slice(0, 4): print("  pav x=", v[0], "..", v[1], " y=", v[2], "..", v[3])
	var lo := 1e9; var hi := -1e9
	for v in wall:
		if v[0] > 4.0: lo = minf(lo, v[0])
		if v[1] < -4.0: hi = maxf(hi, v[1])
	print("nearest wall +x=", snappedf(lo,0.01), "  nearest wall -x=", snappedf(hi,0.01))
	print("WALK_DONE")
	quit()
