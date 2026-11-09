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
	var buckets := {}
	var total := 0
	for n in main.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if not mi.is_visible_in_tree(): continue
		total += 1
		var root_name := ""
		var cur: Node = mi
		while cur != null and cur.get_parent() != main:
			cur = cur.get_parent()
		if cur != null: root_name = String(cur.name)
		if root_name == "":
			root_name = String(mi.name)
		buckets[root_name] = int(buckets.get(root_name, 0)) + 1
	var keys := buckets.keys()
	keys.sort()
	print("TOTAL ", total)
	for k in keys:
		print("  ", k, " = ", buckets[k])
	print("BREAKDOWN_DONE")
	quit()
