extends SceneTree
const Mats=preload("res://scripts/environment_materials.gd")
func _initialize() -> void:
	for index in range(12):
		var road=load("res://assets/models/environment/city_hd_%02d.glb"%index).instantiate()
		Mats.apply(road)
		print("--- BLOCK ",index," ---")
		_inspect(road)
		road.free()
	quit()
func _inspect(node: Node) -> void:
	if node is MeshInstance3D:
		for i in range(node.mesh.get_surface_count()):
			var m=node.mesh.surface_get_material(i)
			if m and m.resource_name.begins_with("PBR"):
				var live=node.get_surface_override_material(i)
				print(m.resource_name," override=",live!=null," texture=",live.albedo_texture.get_size() if live and live.albedo_texture else Vector2i.ZERO)
	for child in node.get_children(): _inspect(child)
