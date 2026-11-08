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
	await create_timer(1.0).timeout
	var ls = main.get("lobby")
	for m in ls.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null: continue
		var a: AABB = mi.get_aabb()
		var mat := mi.get_active_material(0)
		var col := "null"
		if mat is StandardMaterial3D:
			col = str((mat as StandardMaterial3D).albedo_color)
		if a.size.x > 1.5 and a.size.y < 0.5:
			print("MESH ", mi.name, " size=", a.size, " y=", snappedf(mi.global_position.y, 0.01), " col=", col)
	print("LM_DONE")
	quit()
