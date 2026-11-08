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
	await create_timer(0.6).timeout
	var ls = main.get("lobby")
	for i in range(ls.PETS.size()):
		ls.call("show_pet", ls.PETS[i].asset)
		await create_timer(0.5).timeout
		var pet = ls.get("pet")
		if pet == null:
			print("PET ", i, " none"); continue
		var box := AABB(); var first := true
		for m in pet.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			if mi.mesh == null: continue
			var a: AABB = mi.global_transform * mi.get_aabb()
			box = a if first else box.merge(a); first = false
		print("PET ", i, " ", ls.PETS[i].name, " size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)), " scale=", snappedf(pet.scale.x,0.01))
	print("PS_DONE")
	quit()
