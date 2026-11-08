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
	await create_timer(0.4).timeout
	main.call("set_lobby_tab", 0)
	main.call("_lobby_tap", (main.call("lobby_card_rect", 1) as Rect2).get_center())
	await create_timer(0.9).timeout
	var lobby = main.get("lobby")
	var a = lobby.get("actor")
	print("actor valid=", a != null and is_instance_valid(a))
	if a != null and is_instance_valid(a):
		print("actor name=", a.name, " pos=", a.position, " scale=", a.scale, " visible=", a.visible)
		var box := AABB(); var first := true
		for mi in a.find_children("*","MeshInstance3D",true,false):
			var m: MeshInstance3D = mi
			if m.mesh == null: continue
			var b: AABB = m.global_transform * m.get_aabb()
			box = b if first else box.merge(b)
			first = false
		print("actor world aabb=", box)
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://tools/riley_stage2.png")
	print("RILEY3_DONE")
	quit()
