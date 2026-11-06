extends SceneTree
func _initialize() -> void:
	for v in [2,5,9,11,16,17,23]:
		var p: String="res://assets/models/environment/city_hd_%02d.glb"%v
		var n: Node3D=(load(p) as PackedScene).instantiate()
		var z: Node=n.find_child("CITY_zebra_paint",true,false)
		print("VARIANT ",v," zebra_node=",z!=null)
		n.free()
	quit()
