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
	# anchor: the red hand wheel is the biggest red round thing near the door
	var wheel_center := Vector3.ZERO
	var best := 0.0
	for mi in safe.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null: continue
		var a: AABB = m.global_transform * m.get_aabb()
		var s := a.size
		if absf(s.x-s.y) < 0.1 and absf(s.y-s.z) < 0.1 and s.x > best and s.x > 0.4 and s.x < 1.2:
			best = s.x; wheel_center = a.get_center()
	print("WHEEL? size=", snappedf(best,0.01), " at=", wheel_center)
	for mi in safe.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null or not m.is_visible_in_tree(): continue
		var a: AABB = m.global_transform * m.get_aabb()
		if a.get_center().distance_to(wheel_center) < 0.9 and a.size.x < 0.6:
			print("DOOR_OBJ ", m.name, " size=", a.size, " dist=", snappedf(a.get_center().distance_to(wheel_center),2))
	print("DOOR_DONE")
	quit()
