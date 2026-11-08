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
	for nm in ["Safe_night","Safe_glass","Safe_brick"]:
		var mi := ls.find_child(nm, true, false) as MeshInstance3D
		if mi == null: continue
		var a: AABB = mi.global_transform * mi.get_aabb()
		print(nm, " global_pos=", Vector3(snappedf(a.position.x,0.01),snappedf(a.position.y,0.01),snappedf(a.position.z,0.01)),
			" size=", Vector3(snappedf(a.size.x,0.01),snappedf(a.size.y,0.01),snappedf(a.size.z,0.01)))
	print("CAM=", (main.get("camera") as Camera3D).global_position)
	print("WINS_DONE")
	quit()
