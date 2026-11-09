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
	await create_timer(0.5).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(1.2).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(4.0).timeout
	var found := 0
	for n in main.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null or not mi.is_visible_in_tree(): continue
		var box: AABB = mi.global_transform * mi.get_aabb()
		var span := maxf(box.size.x, maxf(box.size.y, box.size.z))
		if span < 25.0: continue
		var mat := mi.get_surface_override_material(0)
		if mat == null and mi.mesh.get_surface_count() > 0:
			mat = mi.mesh.surface_get_material(0)
		var col := Color.WHITE
		if mat is StandardMaterial3D: col = (mat as StandardMaterial3D).albedo_color
		if span > 40.0 or col.g > col.r + 0.12:
			found += 1
			print("BIG ", mi.name, " span=", snappedf(span,0.1), " color=", col, " parent=", mi.get_parent().name)
	print("BIG_TOTAL ", found)
	print("GREEN_DONE")
	quit()
