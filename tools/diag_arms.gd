extends SceneTree

# Arm close-up: same lobby pose pipeline as diag_bust, framed waist-up so the elbow
# and hand orientation are visible. Usage: --script tools/diag_arms.gd -- twist=10
# Renders riley at several palm-twist values for side-by-side comparison.

const ArmsRelaxed := preload("res://scripts/arms_relaxed.gd")
const GunGripIK := preload("res://scripts/gun_grip_ik.gd")
const ModelFix := preload("res://scripts/model_fix.gd")

var camera: Camera3D
var actor: Node3D
var world: Node3D

func _initialize() -> void:
	call_deferred("_run")

func _shot(tag: String) -> void:
	await create_timer(0.35).timeout
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://diagnostics/render-diag/" + tag + ".png")

func _run() -> void:
	var twists: Array[float] = [0.0]
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("twist="):
			twists.clear()
			for part in arg.trim_prefix("twist=").split(","):
				twists.append(float(part))
	root.size = Vector2i(540, 720)
	world = Node3D.new(); root.add_child(world)
	var env := WorldEnvironment.new(); world.add_child(env)
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.15, 0.17, 0.19)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.8, 0.85, 0.9)
	env.environment.ambient_light_energy = 0.7
	var key := DirectionalLight3D.new(); world.add_child(key)
	key.rotation_degrees = Vector3(-32, -25, 0)
	key.light_energy = 1.15
	camera = Camera3D.new(); world.add_child(camera); camera.current = true
	camera.position = Vector3(0.0, 1.05, 1.85)
	camera.look_at(Vector3(0, 0.88, 0))
	camera.fov = 38
	for twist in twists:
		actor = (load("res://assets/models/actors/survivor_riley_universal.glb") as PackedScene).instantiate() as Node3D
		world.add_child(actor)
		ModelFix.double_sided(actor)
		var skeleton := actor.find_child("Skeleton3D", true, false) as Skeleton3D
		skeleton.reset_bone_poses()
		var arms := ArmsRelaxed.new()
		arms.body = actor
		arms.hand_offset = {"r": GunGripIK.mesh_offset(actor, "hand_r"), "l": GunGripIK.mesh_offset(actor, "hand_l")}
		arms.setup_from_model(actor, skeleton)
		arms.palm_twist_deg = twist
		arms.outward = 0.06
		arms.forward = 0.03
		arms.clavicle_drop = 5.0
		arms.base_bend = 14.0
		skeleton.add_child(arms)
		await _shot("riley-arms-twist" + str(int(twist)))
		actor.queue_free(); await process_frame
	print("ARMS_CAPTURE_DONE")
	quit()
