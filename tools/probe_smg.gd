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
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.6).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	var p = main.get("player")
	p.call("set_weapon", "SMG")
	await create_timer(0.5).timeout
	var wm = p.get("weapon_model")
	var box = AABB(); var first = true
	for m in wm.find_children("*", "MeshInstance3D", true, false):
		var x = m as MeshInstance3D
		if x.mesh == null: continue
		var a: AABB = x.global_transform * x.get_aabb()
		box = a if first else box.merge(a); first = false
	print("SMG size=", Vector3(snappedf(box.size.x,0.01),snappedf(box.size.y,0.01),snappedf(box.size.z,0.01)))
	print("SMG_DONE")
	quit()
