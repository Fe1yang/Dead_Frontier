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
		var mat := mi.get_active_material(0)
		var n := ""
		if mat: n = mat.resource_name
		if n in ["SafeGlass","SafeNight","SafeMoon","SafeGlassAmber"]:
			var a: AABB = mi.global_transform * mi.get_aabb()
			print("WIN ", n, " node=", mi.name, " pos=", Vector3(snappedf(a.position.x,0.1),snappedf(a.position.y,0.1),snappedf(a.position.z,0.1)), " size=", Vector3(snappedf(a.size.x,0.1),snappedf(a.size.y,0.1),snappedf(a.size.z,0.1)))
	print("WIN_DONE")
	quit()
