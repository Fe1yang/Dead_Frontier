extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var r = load("res://scripts/barrel_roll_3d.gd").new()
	root.add_child(r)
	await process_frame
	await process_frame
	_dump(r, 0)
	print("TREE_DONE")
	quit()
func _dump(n: Node, depth: int) -> void:
	var pad := ""
	for i in range(depth): pad += "  "
	var extra := ""
	if n is MeshInstance3D:
		var m: MeshInstance3D = n
		extra = " mesh=" + (str(m.mesh.resource_path) if m.mesh else "null") + " surf=" + str(m.mesh.get_surface_count() if m.mesh else -1)
	print(pad, n.name, " [", n.get_class(), "]", extra)
	for c in n.get_children(): _dump(c, depth + 1)
