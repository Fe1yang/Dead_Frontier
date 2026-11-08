extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.4).timeout
	main.set("character_choice", 4)
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	await create_timer(0.4).timeout
	var p = main.get("player")
	var wm = p.get("weapon_model")
	var origin: Vector3 = wm.global_position
	var box = AABB(); var first = true
	for m in wm.find_children("*", "MeshInstance3D", true, false):
		var x = m as MeshInstance3D
		if x.mesh == null: continue
		var a: AABB = x.global_transform * x.get_aabb()
		box = a if first else box.merge(a); first = false
	var c: Vector3 = box.position + box.size * 0.5
	print("ORIGIN=", Vector3(snappedf(origin.x,0.01),snappedf(origin.y,0.01),snappedf(origin.z,0.01)))
	print("MESH CENTRE=", Vector3(snappedf(c.x,0.01),snappedf(c.y,0.01),snappedf(c.z,0.01)))
	print("OFFSET=", Vector3(snappedf(c.x-origin.x,0.01),snappedf(c.y-origin.y,0.01),snappedf(c.z-origin.z,0.01)))
	print("SIZE=", Vector3(snappedf(box.size.x,0.01),snappedf(box.size.y,0.01),snappedf(box.size.z,0.01)))
	print("GBOX_DONE")
	quit()
