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
		var a: AABB = mi.global_transform * mi.get_aabb()
		if absf(a.position.x) < 5.0 and absf(a.end.x) < 9.0 and a.size.y > 1.2 and a.size.y < 4.0:
			var nm := String(mi.name)
			if not seen.has(nm):
				seen[nm] = "x=" + str(snappedf(a.position.x,0.1)) + ".." + str(snappedf(a.end.x,0.1)) + " z=" + str(snappedf(a.position.z,0.1)) + " y=" + str(snappedf(a.end.y,0.1))
	var k := seen.keys()
	k.sort()
	for key in k.slice(0, 25):
		print(key, "  ", seen[key])
	print("NM_DONE")
	quit()
