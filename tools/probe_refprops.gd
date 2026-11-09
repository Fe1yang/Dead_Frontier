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
	var seen := {}
	for m in road.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		var nm := String(mi.name)
		var key := ""
		for k in ["lamp", "soil", "weed", "tree", "bin", "bench", "planter", "paint"]:
			if nm.to_lower().find(k) != -1: key = k; break
		if key == "": continue
		var a: AABB = mi.global_transform * mi.get_aabb()
		var cur: Array = seen.get(key, [1e9, -1e9, 1e9, -1e9])
		seen[key] = [minf(cur[0], a.position.x), maxf(cur[1], a.end.x), minf(cur[2], a.position.y), maxf(cur[3], a.end.y)]
	for k in seen.keys():
		var v: Array = seen[k]
		print(k, " x=", snappedf(v[0],0.01), "..", snappedf(v[1],0.01), " y=", snappedf(v[2],0.01), "..", snappedf(v[3],0.01))
	print("REF_DONE")
	quit()
