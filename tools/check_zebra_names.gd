extends SceneTree
func _initialize() -> void:
	for v in [5,16]:
		var p: String="res://assets/models/environment/city_hd_%02d.glb"%v
		var n: Node3D=(load(p) as PackedScene).instantiate()
		var names: Array=[]
		for c in n.get_children(): names.append(c.name)
		print("VARIANT ",v," children: ",names)
		n.free()
	quit()
