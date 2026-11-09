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
	await create_timer(0.2).timeout
	main.set("loadout_on", false); main.set("owned_vehicle", "")
	main.call("start_run", true, true)
	await create_timer(0.4).timeout
	if String(main.get("state")) == "intro":
		main.call("_finish_intro")
	main.set("spawn_timer", 1.0e9)
	main.call("_spawn_zombie", -8.0, "jockey")
	await create_timer(0.9).timeout
	for z in (main.get("zombies") as Array):
		if is_instance_valid(z) and String(z.get("kind")) == "jockey":
			print("JOCKEY gait=", z.get("gait") != null, " clip=", (z.get("animation_player") as AnimationPlayer).current_animation if z.get("animation_player") else "none")
			var box := AABB(); var first := true
			for mi in z.find_children("*","MeshInstance3D",true,false):
				var m: MeshInstance3D = mi
				if m.mesh == null: continue
				var b: AABB = m.global_transform * m.get_aabb()
				box = b if first else box.merge(b)
				first = false
			print("JOCKEY size=", box.size)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/jockey_quad.png")
	print("JOCKEY3_DONE")
	quit()
