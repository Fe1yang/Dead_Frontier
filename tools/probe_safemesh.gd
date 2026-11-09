extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(1.2).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.8).timeout
	var ls = main.get("lobby")
	var safe = ls.find_child("SafehouseInterior", true, false)
	if safe == null:
		print("NO_SAFEHOUSE")
		quit()
		return
	for mi in safe.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null or not m.is_visible_in_tree():
			continue
		var a: AABB = m.global_transform * m.get_aabb()
		var s := a.size
		var roundish := absf(s.x - s.y) < 0.12 and absf(s.y - s.z) < 0.12
		if roundish and s.x > 0.18 and s.x < 0.9:
			print("BALL?", m.name, " size=", Vector3(snappedf(s.x,0.01),snappedf(s.y,0.01),snappedf(s.z,0.01)), " at=", a.get_center())
	print("SAFE_DONE")
	quit()
