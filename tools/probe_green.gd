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
		var mat := mi.get_active_material(0) as StandardMaterial3D
		if mat == null: continue
		var c := mat.albedo_color
		if c.g > c.r and c.g > c.b and c.g > 0.12:
			var a: AABB = mi.global_transform * mi.get_aabb()
			print("GREEN ", mi.name, " mat=", mat.resource_name, " col=", c,
				" pos=", Vector3(snappedf(a.position.x,0.01),snappedf(a.position.y,0.01),snappedf(a.position.z,0.01)),
				" size=", Vector3(snappedf(a.size.x,0.01),snappedf(a.size.y,0.01),snappedf(a.size.z,0.01)))
	print("GREEN_DONE")
	quit()
