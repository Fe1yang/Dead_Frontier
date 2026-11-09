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
	var road = (main.get("roads") as Array)[3]
	print("district scale=", road.scale, " pos=", road.position)
	var names := {}
	for n in road.get_children():
		var nm := String(n.name)
		if nm.begins_with("phone_booth") or nm.begins_with("bench") or nm.begins_with("trash"):
			names[nm] = snappedf(n.global_position.x, 0.01)
	var k := names.keys()
	k.sort()
	for key in k.slice(0, 6): print("  ", key, " world_x=", names[key])
	print("PX_DONE")
	quit()
