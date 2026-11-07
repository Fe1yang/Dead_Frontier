extends SceneTree
# Renders the safehouse GLB from the ACTUAL lobby solo camera (pet_zoom=0) with flat
# per-object colors, 540x960 portrait, so regions from a real game screenshot map 1:1.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(540, 960)
	var world := Node3D.new(); root.add_child(world)
	var env := WorldEnvironment.new(); world.add_child(env)
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.05, 0.05, 0.06)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.75, 0.78, 0.82)
	env.environment.ambient_light_energy = 0.85
	var camera := Camera3D.new(); world.add_child(camera); camera.current = true
	camera.position = Vector3(-0.08, 0.92, 4.15)
	camera.look_at(Vector3(-0.08, 0.50, 0.0))
	camera.fov = 38.0
	var packed := load("res://assets/models/environment/safehouse_interior.glb") as PackedScene
	var safe := packed.instantiate() as Node3D
	world.add_child(safe)
	var rng := RandomNumberGenerator.new(); rng.seed = 1234
	for m in safe.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color.from_hsv(rng.randf(), 0.75, 0.9)
		mi.material_override = mat
		print("COLOR %s #%02x%02x%02x" % [mi.name, mat.albedo_color.r8, mat.albedo_color.g8, mat.albedo_color.b8])
	await create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/lobbycam-colors.png")
	print("LOBBYCAM_DONE")
	quit()
