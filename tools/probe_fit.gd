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
	main.set("loadout_on", false)
	main.call("start_run", true, true)
	await create_timer(1.0).timeout
	var p = main.get("player")
	p.call("set_armor", true)
	p.call("set_helmet", true)
	await create_timer(0.5).timeout

	var am = p.get("armor_model")
	var hm = p.get("helmet_model")
	for pair in [["armor", am], ["helmet", hm]]:
		var node = pair[1]
		if node == null or not is_instance_valid(node):
			print(pair[0], " missing")
			continue
		var box := AABB()
		var first := true
		for m in node.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a)
			first = false
		var body := p.global_position
		print(pair[0], " size=", Vector3(snappedf(box.size.x, 0.01), snappedf(box.size.y, 0.01), snappedf(box.size.z, 0.01)),
			" centre_y=", snappedf(box.get_center().y - body.y, 0.01))
	print("FIT_DONE")
	quit()
