import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# --- state + builder -------------------------------------------------------------------------
if "var flame_jet" not in t:
    anchor = "var weapon_model: Node3D"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## Forward flame jet for the flamethrower (only built when that weapon is equipped).\nvar flame_jet: CPUParticles3D\nvar flame_jet_timer := 0.0", 1)

builder = '''## A real forward jet: a cone of flame particles that leaves the nozzle in the aim direction.
func _build_flame_jet() -> void:
	if is_instance_valid(flame_jet):
		return
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1.0, 0.96, 0.72, 0.0))
	ramp.add_point(0.12, Color(1.0, 0.93, 0.55, 0.95))
	ramp.add_point(0.38, Color(1.0, 0.55, 0.12, 0.85))
	ramp.add_point(0.70, Color(0.85, 0.22, 0.05, 0.45))
	ramp.set_color(3, Color(0.18, 0.14, 0.12, 0.0))
	var jet := CPUParticles3D.new()
	jet.amount = 56
	jet.lifetime = 0.62
	jet.preprocess = 0.05
	jet.local_coords = false
	jet.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	jet.emission_sphere_radius = 0.055
	jet.direction = Vector3(0, 0, -1)
	jet.spread = 7.0
	jet.gravity = Vector3(0, 1.6, 0)
	jet.initial_velocity_min = 9.5
	jet.initial_velocity_max = 14.0
	jet.scale_amount_min = 0.55
	jet.scale_amount_max = 1.5
	jet.color_ramp = ramp
	var quad := QuadMesh.new()
	quad.size = Vector2(0.42, 0.42)
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load("res://assets/vfx/flame_particle.png")
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.vertex_color_use_as_albedo = true
	quad.material = mat
	jet.mesh = quad
	jet.emitting = false
	add_child(jet)
	flame_jet = jet


## Called by the game while the trigger is held: keeps the jet alive for a moment.
func pulse_flame() -> void:
	_build_flame_jet()
	if not is_instance_valid(flame_jet):
		return
	flame_jet_timer = 0.18
	flame_jet.emitting = true
	var from := muzzle_position()
	var dir := aim_direction if aim_direction.length() > 0.01 else Vector3.FORWARD
	flame_jet.global_position = from
	flame_jet.look_at(from + dir * 6.0, Vector3.UP)


'''
anchor2 = "func _load_weapon_model() -> void:"
assert t.count(anchor2) == 1
t = t.replace(anchor2, builder + anchor2, 1)

# stop the jet shortly after the trigger is released
old_tick = "\tflame_jet_timer"  # placeholder guard, replaced below
if "flame_jet_timer = maxf" not in t:
    tick_anchor = "func tick(delta: float) -> void:\n\t_tick_vehicle_visual(delta)"
    assert t.count(tick_anchor) == 1
    t = t.replace(
        tick_anchor,
        "func tick(delta: float) -> void:\n"
        "\tif is_instance_valid(flame_jet) and flame_jet.emitting:\n"
        "\t\tflame_jet_timer = maxf(0.0, flame_jet_timer - delta)\n"
        "\t\tif flame_jet_timer <= 0.0:\n"
        "\t\t\tflame_jet.emitting = false\n"
        "\t_tick_vehicle_visual(delta)",
        1,
    )

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame jet built into player_3d")
