extends SceneTree

# 只读诊断：不动任何资产文件，按游戏 main_3d.gd 的阳光参数布光，
# 对 riley / maya 分别拍 基准 / 关阴影 / 关法线贴图 / 全关 四张脸特写。

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
	DirAccess.make_dir_recursive_absolute("res://diagnostics/render-diag")
	root.size = Vector2i(720, 720)
	world = Node3D.new(); root.add_child(world)
	var env := WorldEnvironment.new(); world.add_child(env)
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.12, 0.15, 0.17)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.78, 0.84, 0.90)
	env.environment.ambient_light_energy = 0.65
	# 游戏 main_3d.gd 阳光参数
	key = DirectionalLight3D.new(); world.add_child(key)
	key.rotation_degrees = Vector3(-32, -28, 0)
	key.light_energy = 1.25
	key.shadow_enabled = true
	key.shadow_bias = 0.035
	key.shadow_normal_bias = 0.65
	key.shadow_blur = 1.45
	key.shadow_opacity = 0.76
	key.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
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
		for m in materials:
			print("DIAG_MAT ", tag, " normal=", m.normal_enabled, " scale=", m.normal_scale,
				" tex_filter=", m.texture_filter, " cull=", m.cull_mode, " shading=", m.shading_mode)
		await _shot(tag, "baseline")
		key.shadow_enabled = false
		await _shot(tag, "noshadow")
		key.shadow_enabled = true
		for m in materials: m.normal_enabled = false
		await _shot(tag, "nonormal")
		key.shadow_enabled = false
		await _shot(tag, "clean")
	print("RENDER_DIAG_DONE")
	quit()
