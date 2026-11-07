extends SceneTree
# Renders the safehouse interior GLB alone from the lobby camera, no character or UI,
# to locate a prop for removal. Usage: --script tools/diag_safehouse.gd

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
	var key := DirectionalLight3D.new(); world.add_child(key)
	key.rotation_degrees = Vector3(-35, -20, 0); key.light_energy = 1.4
	var camera := Camera3D.new(); world.add_child(camera); camera.current = true
	camera.position = Vector3(0.0, 1.22, 5.7)
	camera.look_at(Vector3(0.0, 0.62, 0.0))
	camera.fov = 38.0
	var packed := load("res://assets/models/environment/safehouse_interior.glb") as PackedScene
	var safe := packed.instantiate() as Node3D
	world.add_child(safe)
	# Flat unshaded color per object so merged furniture can be told apart.
	var rng := RandomNumberGenerator.new(); rng.seed = 1234
	for m in safe.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = Color.from_hsv(rng.randf(), 0.75, 0.9)
		mi.material_override = mat
		print("COLOR %s #%02x%02x%02x" % [mi.name, mat.albedo_color.r8, mat.albedo_color.g8, mat.albedo_color.b8])
	await create_timer(0.6).timeout
	# Front view: the full set from the lobby camera.
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/safehouse-wide.png")
	# Right close-up: frame the circled shelf region (world x 1.2..3.2, y 0..2.2).
	camera.position = Vector3(2.2, 1.1, 2.6)
	camera.look_at(Vector3(2.2, 0.9, -2.0))
	camera.fov = 50.0
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/safehouse-right.png")
	# Left close-up for reference.
	camera.position = Vector3(-2.2, 1.1, 2.6)
	camera.look_at(Vector3(-2.2, 0.9, -2.0))
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/safehouse-left.png")
	print("SAFEHOUSE_SHOT_DONE")
	quit()
