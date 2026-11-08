extends SceneTree
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var c = load("res://assets/models/vehicles/black_car.glb").instantiate()
	root.add_child(c)
	await process_frame
	for mi in c.find_children("*", "MeshInstance3D", true, false):
		var m: MeshInstance3D = mi
		if m.mesh == null: continue
		print("MESH ", m.name, " surfaces=", m.mesh.get_surface_count())
		for s in range(m.mesh.get_surface_count()):
			var mat = m.mesh.surface_get_material(s)
			if mat is BaseMaterial3D:
				var bm: BaseMaterial3D = mat
				print("   surface ", s, " mat=", bm.resource_name, " albedo=", bm.albedo_color, " metallic=", bm.metallic, " rough=", bm.roughness, " transp=", bm.transparency, " tex=", bm.albedo_texture != null)
			else:
				print("   surface ", s, " mat=", mat)
	print("MATS_DONE")
	quit()
