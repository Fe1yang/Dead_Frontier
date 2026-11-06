extends SceneTree

var camera: Camera3D
var actor: Node3D
var world: Node3D

func _initialize() -> void:
	call_deferred("_run")

func _shot(tag: String, variant: String) -> void:
	await create_timer(0.2).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/" + tag + "-" + variant + ".png")

func _run() -> void:
	root.size = Vector2i(480, 720)
	world = Node3D.new(); root.add_child(world)
	var env := WorldEnvironment.new(); world.add_child(env)
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.16, 0.18, 0.20)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.8, 0.85, 0.9)
	env.environment.ambient_light_energy = 0.7
	var key := DirectionalLight3D.new(); world.add_child(key)
	key.rotation_degrees = Vector3(-35, -25, 0)
	key.light_energy = 1.1
	camera = Camera3D.new(); world.add_child(camera); camera.current = true
	camera.position = Vector3(0.0, 1.05, 2.6)
	camera.look_at(Vector3(0, 0.95, 0))
	camera.fov = 35
	for tag in ["riley", "maya"]:
		if is_instance_valid(actor): actor.queue_free(); await process_frame
		actor = (load("res://assets/models/actors/survivor_" + tag + "_universal.glb") as PackedScene).instantiate() as Node3D
		world.add_child(actor)
		await _shot(tag, "lobby-rest")
		var ap := actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
		if ap and ap.has_animation("Run_Gun_F"):
			ap.play("Run_Gun_F")
			ap.seek(0.35, true)
			ap.advance(0.0)
			await _shot(tag, "run-f")
	print("LOBBY_DIAG_DONE")
	quit()
