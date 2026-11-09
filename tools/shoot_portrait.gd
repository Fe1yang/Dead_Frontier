extends SceneTree

var model: Node3D
var cam: Camera3D

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var asset := String(OS.get_environment("SHOT_ASSET"))
	var out_path := String(OS.get_environment("SHOT_OUT"))
	var yaw := float(OS.get_environment("SHOT_YAW"))   # radians, 0 = model's own front
	var dist := float(OS.get_environment("SHOT_DIST"))

	var world := Node3D.new()
	root.add_child(world)

	var packed := load(asset) as PackedScene
	if packed == null:
		print("SHOT_FAIL load ", asset)
		quit()
		return
	model = packed.instantiate() as Node3D
	world.add_child(model)
	await process_frame

	# a plain, evenly lit studio: no cracks are hidden, this is the model itself
	var key := DirectionalLight3D.new()
	key.rotation_degrees = Vector3(-18.0, 12.0, 0.0)
	key.light_energy = 1.35
	key.shadow_enabled = false
	world.add_child(key)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-6.0, 200.0, 0.0)
	fill.light_energy = 0.55
	world.add_child(fill)

	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.09, 0.10, 0.11)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.55, 0.56, 0.6)
	e.ambient_light_energy = 0.55
	env.environment = e
	world.add_child(env)

	var box := AABB()
	var first := true
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m == null or m.mesh == null:
			continue
		var a: AABB = m.global_transform * m.get_aabb()
		box = a if first else box.merge(a)
		first = false
	print("BOUNDS ", box.position, " size ", box.size)

	var top := box.position.y + box.size.y
	var centre_x := box.get_center().x
	# head to chest: the head occupies the top ~0.26 m of the body
	var aim_y := top - 0.22
	cam = Camera3D.new()
	cam.fov = 30.0
	world.add_child(cam)
	var dir := Vector3(sin(yaw), 0.0, cos(yaw))
	cam.global_position = Vector3(centre_x, aim_y + 0.02, 0.0) + dir * dist
	cam.look_at(Vector3(centre_x, aim_y, 0.0), Vector3.UP)
	cam.current = true

	await process_frame
	await RenderingServer.frame_post_draw
	root.get_viewport().get_texture().get_image().save_png(out_path)
	print("SHOT ", out_path, " yaw=", yaw, " dist=", dist, " aim_y=", aim_y)
	print("PORTRAIT_DONE")
	quit()
