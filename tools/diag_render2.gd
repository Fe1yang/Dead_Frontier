extends SceneTree

var camera: Camera3D
var actor: Node3D
var world: Node3D
var key: DirectionalLight3D

func _initialize() -> void:
	call_deferred("_run")

func _materials(node: Node, output: Array) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			if material is StandardMaterial3D:
				output.append(material)
	for child in node.get_children():
		_materials(child, output)

func _shot(tag: String, variant: String) -> void:
	await create_timer(0.2).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/" + tag + "-" + variant + ".png")

func _run() -> void:
	root.size = Vector2i(720, 720)
	world = Node3D.new(); root.add_child(world)
	var env := WorldEnvironment.new(); world.add_child(env)
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.12, 0.15, 0.17)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.78, 0.84, 0.90)
	env.environment.ambient_light_energy = 0.65
	key = DirectionalLight3D.new(); world.add_child(key)
	key.rotation_degrees = Vector3(-32, -28, 0)
	key.light_energy = 1.25
	key.shadow_enabled = false
	camera = Camera3D.new(); world.add_child(camera); camera.current = true; camera.fov = 30
	for tag in ["riley", "maya"]:
		if is_instance_valid(actor): actor.queue_free(); await process_frame
		actor = (load("res://assets/models/actors/survivor_" + tag + "_universal.glb") as PackedScene).instantiate() as Node3D
		world.add_child(actor)
		var skeleton := actor.find_child("Skeleton3D", true, false) as Skeleton3D
		var head_index := skeleton.find_bone("Head")
		if head_index < 0: head_index = skeleton.find_bone("head")
		var head_pos := skeleton.to_global(skeleton.get_bone_global_pose(head_index).origin)
		camera.position = head_pos + Vector3(0.10, 0.02, 0.85)
		camera.look_at(head_pos + Vector3(0, 0.015, 0))
		var materials: Array = []; _materials(actor, materials)
		# 无光照纯贴图：瑕疵还在 = 贴图/几何层级；消失 = 光照/法线层级
		for m in materials: m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		await _shot(tag, "unshaded")
		for m in materials:
			m.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		await _shot(tag, "doublesided")
	print("UNSHADED_DIAG_DONE")
	quit()
