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
	for r in (main.get("roads") as Array):
		for c in r.get_children():
			if not String(c.name).begins_with("phone_booth"): continue
			var meshes: Array = c.find_children("*", "MeshInstance3D", true, false)
			var box := AABB(); var first := true
			for m in meshes:
				var mi := m as MeshInstance3D
				if mi.mesh == null: continue
				var a: AABB = mi.global_transform * mi.get_aabb()
				box = a if first else box.merge(a); first = false
			print("booth visible=", c.visible, " meshes=", meshes.size(), " size=", box.size, " at=", c.global_position)
			quit()
			return
	print("NO_BOOTH")
	quit()
