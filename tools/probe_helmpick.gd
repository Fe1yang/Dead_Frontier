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
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9); main.set("crate_timer", 1.0e9)
	main.call("_spawn_pickup", "helmet", -6.0)
	await create_timer(0.5).timeout
	var pk = (main.get("pickups") as Array).back()
	var mi = pk.get("model_instance")
	var box = AABB(); var first = true
	for m in mi.find_children("*", "MeshInstance3D", true, false):
		var x = m as MeshInstance3D
		if x.mesh == null: continue
		var a: AABB = x.global_transform * x.get_aabb()
		box = a if first else box.merge(a); first = false
	print("HELMET size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)), " scale=", mi.scale.x)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/helmet_pickup.png")
	print("HELMPICK_DONE")
	quit()
