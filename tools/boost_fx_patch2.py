import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

if "boost_fx" not in "\n".join(lines):
    idx = next(i for i, l in enumerate(lines) if l.startswith("var flame_jet: CPUParticles3D"))
    lines[idx + 1:idx + 1] = [
        "## Exhaust behind a fast vehicle (the gold car's dash).",
        "var boost_fx: CPUParticles3D",
    ]

data = "\n".join(lines)

if "func _build_boost" not in data:
    builder = '''## Rear exhaust: dust and heat sparks trailing the car while it is at speed.
func _build_boost() -> void:
	if is_instance_valid(boost_fx):
		return
	var g := Gradient.new()
	g.set_color(0, Color(0.85, 0.82, 0.76, 0.0))
	g.add_point(0.15, Color(0.80, 0.77, 0.70, 0.55))
	g.add_point(0.55, Color(0.55, 0.52, 0.48, 0.30))
	g.set_color(3, Color(0.30, 0.28, 0.26, 0.0))
	var fx := CPUParticles3D.new()
	fx.amount = 90
	fx.lifetime = 0.55
	fx.local_coords = false
	fx.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	fx.emission_box_extents = Vector3(0.55, 0.12, 0.05)
	fx.direction = Vector3(0, 0, 1)
	fx.spread = 14.0
	fx.gravity = Vector3(0, 0.6, 0)
	fx.initial_velocity_min = 3.0
	fx.initial_velocity_max = 6.5
	fx.scale_amount_min = 0.35
	fx.scale_amount_max = 1.0
	fx.color_ramp = g
	var quad := QuadMesh.new()
	quad.size = Vector2(0.34, 0.34)
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load("res://assets/vfx/flame_particle.png")
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.vertex_color_use_as_albedo = true
	quad.material = mat
	fx.mesh = quad
	fx.emitting = false
	add_child(fx)
	boost_fx = fx


'''
    anchor = "func _tick_vehicle_visual(delta: float) -> void:"
    assert data.count(anchor) == 1
    data = data.replace(anchor, builder + anchor, 1)

if "boost_fx.emitting = true" not in data:
    anchor2 = "func _tick_vehicle_visual(delta: float) -> void:\n\tif not is_instance_valid(vehicle_model): return"
    assert data.count(anchor2) == 1, data.count(anchor2)
    inject = (
        "func _tick_vehicle_visual(delta: float) -> void:\n"
        "\tif not is_instance_valid(vehicle_model): return\n"
        "\t# Exhaust sits at the tail of the car and only fires while the run is moving fast.\n"
        "\tvar vstat: Dictionary = VEHICLE_STATS.get(vehicle, {})\n"
        "\tif float(vstat.get(\"speed\", 0.0)) >= 3.4:\n"
        "\t\t_build_boost()\n"
        "\t\tif is_instance_valid(boost_fx):\n"
        "\t\t\tboost_fx.global_position = vehicle_model.global_position + Vector3(0, 0.45, 1.15)\n"
        "\t\t\tboost_fx.emitting = true\n"
        "\telif is_instance_valid(boost_fx):\n"
        "\t\tboost_fx.emitting = false"
    )
    data = data.replace(anchor2, inject, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(data)
print("vehicle exhaust wired")
