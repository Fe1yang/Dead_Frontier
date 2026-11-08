extends SceneTree
var main: Node
func _initialize() -> void:
	call_deferred("_run")
func _run() -> void:
	var who := int(OS.get_environment("PET_INDEX")) if OS.get_environment("PET_INDEX") != "" else 5
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(10):
		await process_frame
	main = current_scene
	await create_timer(0.9).timeout
	paused = false
	main.call("enter_lobby")
	await create_timer(0.3).timeout
	var owned = main.get("owned_pets")
	owned[who] = true
	main.set("pet_choice", who)
	main.set("pet_equipped", true)
	main.set("loadout_on", true)
	main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.5).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	await create_timer(1.6).timeout
	var pets = main.get("companion_pets")
	print("PETS spawned=", pets.size())
	if pets.size() > 0:
		var p = pets[0]
		var ap: AnimationPlayer = p.find_child("AnimationPlayer", true, false)
		print("PET clip=", ap.current_animation if ap else "none", " pos=", p.position)
		var box := AABB(); var first := true
		for mi in p.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("PET aabb size=", box.size)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/petrun_%d.png" % who)
	print("PETRUN_DONE ", who)
	quit()
