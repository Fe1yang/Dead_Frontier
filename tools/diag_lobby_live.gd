extends SceneTree
## Boot the REAL game into the lobby, then flat-color every MeshInstance3D under the
## safehouse node and hide the actor, so the color map matches the real game camera 1:1.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(936, 1210)
	change_scene_to_file("res://scenes/main.tscn")
	for i in range(8):
		await process_frame
	var main := current_scene
	if main == null:
		push_error("diag: no main scene"); quit(1); return
	if main.has_method("enter_lobby"):
		main.enter_lobby()
	if main.has_method("select_character"):
		main.select_character(0)
	await create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png("res://diagnostics/render-diag/lobby-live-textured.png")
	# Find the safehouse instance anywhere in the tree.
	var safe: Node = null
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n.name == "SafehouseInterior":
			safe = n; break
		for c in n.get_children():
			stack.append(c)
	if safe == null:
		push_error("diag: safehouse not found"); quit(1); return
	# Grab the live camera (first Camera3D under the scene) for screen-space bboxes.
	var cam: Camera3D = null
	var cs: Array = [root]
	while not cs.is_empty():
		var n2: Node = cs.pop_back()
		if n2 is Camera3D and (n2 as Camera3D).current:
			cam = n2 as Camera3D; break
		for c2 in n2.get_children():
			cs.append(c2)
	if cam == null:
		push_error("diag: no camera"); quit(1); return
	var vp := root.get_viewport().get_visible_rect().size
	var rng := RandomNumberGenerator.new(); rng.seed = 1234
	for m in safe.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color.from_hsv(rng.randf(), 0.75, 0.9)
		mi.material_override = mat
		var aabb := mi.get_aabb()
		var corners: Array[Vector3] = []
		for cx in [aabb.position.x, aabb.end.x]:
			for cy in [aabb.position.y, aabb.end.y]:
				for cz in [aabb.position.z, aabb.end.z]:
					corners.append(mi.to_global(Vector3(cx, cy, cz)))
		var lo := Vector2(1e9, 1e9); var hi := Vector2(-1e9, -1e9)
		for w in corners:
			var s := cam.unproject_position(w)
			lo = Vector2(min(lo.x, s.x), min(lo.y, s.y))
			hi = Vector2(max(hi.x, s.x), max(hi.y, s.y))
		var onscreen := hi.x >= 0.0 and lo.x <= vp.x and hi.y >= 0.0 and lo.y <= vp.y
		print("COLOR %s #%02x%02x%02x scrn x%.0f..%.0f y%.0f..%.0f %s" % [
			mi.name, mat.albedo_color.r8, mat.albedo_color.g8, mat.albedo_color.b8,
			lo.x, hi.x, lo.y, hi.y, "ONSCREEN" if onscreen else "off"])
	# Hide the actor so it doesn't occlude the set.
	var lobby := safe.get_parent()
	if lobby:
		for a in lobby.find_children("*", "Node3D", true, false):
			if a.name == "Actor" or String(a.name).to_lower().contains("actor"):
				a.visible = false
	await create_timer(0.3).timeout
	await RenderingServer.frame_post_draw
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("res://diagnostics/render-diag/lobby-live-colors.png")
	# Elimination pass: candidates whose screen box overlaps the rack region get
	# hidden one at a time; a capture per candidate shows which one IS the rack.
	var rack_rect := Rect2(460, 380, 160, 250)
	var candidates: Array = []
	for m in safe.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var aabb := mi.get_aabb()
		var corners: Array[Vector3] = []
		for cx in [aabb.position.x, aabb.end.x]:
			for cy in [aabb.position.y, aabb.end.y]:
				for cz in [aabb.position.z, aabb.end.z]:
					corners.append(mi.to_global(Vector3(cx, cy, cz)))
		var lo := Vector2(1e9, 1e9); var hi := Vector2(-1e9, -1e9)
		for w in corners:
			var s := cam.unproject_position(w)
			lo = Vector2(min(lo.x, s.x), min(lo.y, s.y))
			hi = Vector2(max(hi.x, s.x), max(hi.y, s.y))
		var r := Rect2(lo, hi - lo)
		if r.intersects(rack_rect) and r.size.y > 60.0:
			candidates.append(mi)
			print("CANDIDATE ", mi.name, " box x%.0f..%.0f y%.0f..%.0f" % [lo.x, hi.x, lo.y, hi.y])
	for mi in candidates:
		mi.visible = false
		await RenderingServer.frame_post_draw
		root.get_viewport().get_texture().get_image().save_png("res://diagnostics/render-diag/lobby-live-hide-%s.png" % mi.name)
		mi.visible = true
	print("LOBBY_LIVE_DONE ", img.get_width(), "x", img.get_height())
	quit()
