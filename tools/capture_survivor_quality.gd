extends SceneTree

var camera: Camera3D
var actor: Node3D

func _initialize() -> void:
	call_deferred("_run")

func _materials(node: Node, output: Array) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			var material: Material=node.get_active_material(surface)
			if material is StandardMaterial3D:
				output.append(material)
	for child in node.get_children(): _materials(child,output)

func _shot(key: String, variant: String) -> void:
	await create_timer(0.15).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/survivors/"+key+"-"+variant+".png")

func _run() -> void:
	DirAccess.make_dir_recursive_absolute("res://diagnostics/survivors")
	root.size=Vector2i(720,720)
	var world:=Node3D.new(); root.add_child(world)
	var environment:=WorldEnvironment.new(); world.add_child(environment)
	environment.environment=Environment.new(); environment.environment.background_mode=Environment.BG_COLOR
	environment.environment.background_color=Color(0.12,0.15,0.17); environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color=Color(0.78,0.84,0.90); environment.environment.ambient_light_energy=0.65
	var key:=DirectionalLight3D.new(); world.add_child(key); key.rotation_degrees=Vector3(-32,-28,0); key.light_energy=1.25
	var fill:=OmniLight3D.new(); world.add_child(fill); fill.position=Vector3(-1.3,1.7,1.4); fill.light_energy=1.0; fill.omni_range=4.0
	camera=Camera3D.new(); world.add_child(camera); camera.current=true; camera.fov=30
	for key_name in ["male","female"]:
		if is_instance_valid(actor): actor.queue_free(); await process_frame
		actor=(load("res://assets/models/actors/survivor_"+key_name+"_universal.glb") as PackedScene).instantiate() as Node3D
		world.add_child(actor)
		var skeleton:=actor.find_child("Skeleton3D",true,false) as Skeleton3D
		var head_index:=skeleton.find_bone("head")
		var head_pos:=skeleton.to_global(skeleton.get_bone_global_pose(head_index).origin)
		camera.position=head_pos+Vector3(0.10,0.02,1.15); camera.look_at(head_pos+Vector3(0,0.015,0))
		var materials: Array=[]; _materials(actor,materials)
		for material in materials:
			print("FACE_MATERIAL ",key_name," normal=",material.normal_enabled," scale=",material.normal_scale," filter=",material.texture_filter)
		await _shot(key_name,"baseline")
		for material in materials:
			material.normal_enabled=false
		await _shot(key_name,"no-normal")
	print("SURVIVOR_QUALITY_CAPTURED")
	quit()
