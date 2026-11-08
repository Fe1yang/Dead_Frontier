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
	main.set("owned_pet", "czech_wolfdog")
	main.call("enter_lobby")
	await create_timer(1.0).timeout
	main.call("set_lobby_tab", 1)
	await create_timer(1.2).timeout
	var ls = main.get("lobby")
	var pet = ls.get("pet")
	if pet:
		var box = AABB(); var first = true
		for m in pet.find_children("*", "MeshInstance3D", true, false):
			var x = m as MeshInstance3D
			if x.mesh == null: continue
			var a: AABB = x.global_transform * x.get_aabb()
			box = a if first else box.merge(a); first = false
		print("PET size=", Vector3(snappedf(box.size.x,0.01), snappedf(box.size.y,0.01), snappedf(box.size.z,0.01)))
		var ap = pet.find_child("AnimationPlayer", true, false)
		print("PET anim=", ap.current_animation if ap else "none")
	else:
		print("PET none")
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/pet_wolf.png")
	print("PET_DONE")
	quit()
