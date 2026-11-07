extends SceneTree
## One-off: shift the safehouse into unobstructed view and hide suspected meshes
## to identify the pale diagonal window boards.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(680, 1210)
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(8):
		await process_frame
	var main := current_scene
	if main == null:
		quit(1); return
	if main.has_method("enter_lobby"):
		main.enter_lobby()
	if main.has_method("select_character"):
		main.select_character(0)
	await create_timer(1.6).timeout
	var safe: Node = null
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n.name == "SafehouseInterior":
			safe = n; break
		for c in n.get_children():
			stack.append(c)
	if safe == null:
		push_error("no safehouse"); quit(1); return
	# Shift the whole set left so the area behind the right UI buttons is visible.
	safe.position.x -= 1.6
	await create_timer(0.4).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://diagnostics/render-diag/window-shifted.png")
	for name in ["Safe_wood_dark", "Safe_paper_old", "Safe_label_cream"]:
		var mi := safe.find_child(name, true, false) as MeshInstance3D
		if mi == null:
			print("MISSING ", name); continue
		mi.visible = false
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://diagnostics/render-diag/window-hide-%s.png" % name)
		mi.visible = true
		print("HIDESHOT ", name)
	print("WINDOW_PROBE_DONE")
	quit()
