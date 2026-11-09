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
	main.set("spawn_timer", 1.0e9)
	var crate = (load("res://scripts/weapon_crate_3d.gd") as GDScript).new()
	main.add_child(crate)
	await process_frame
	for id in ["ARMOR", "HELMET", "SMG"]:
		crate.call("setup", id, 2)
		await process_frame
		await process_frame
		var wm = crate.get("weapon_model")
		if wm == null:
			print(id, " no model"); continue
		var box := AABB(); var first := true
		for m in wm.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print(id, " display size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)))
	print("CS_DONE")
	quit()
