extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var packed := load("res://assets/models/environment/safehouse_interior.glb") as PackedScene
	var safe := packed.instantiate() as Node3D
	root.add_child(safe)
	for name in ["Safe_wood","Safe_wall","Safe_concrete"]:
		var mi := safe.find_child(name, true, false) as MeshInstance3D
		if mi == null:
			print("MISSING ", name); continue
		var mesh := mi.mesh
		print("NODE ", name, " surfaces=", mesh.get_surface_count())
		for i in range(mesh.get_surface_count()):
			var m := mesh.surface_get_material(i)
			if m:
				print("  surf", i, " ", m.resource_name, " albedo=", (m as StandardMaterial3D).albedo_color if m is StandardMaterial3D else m.get_class())
	quit()
