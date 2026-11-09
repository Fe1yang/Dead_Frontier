import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "boost_fx" not in t:
    anchor = "var flame_jet: CPUParticles3D"
    assert t.count(anchor) == 1
    t = t.replace(
        anchor,
        anchor + "\n## Exhaust behind a fast vehicle (the gold car's dash).\nvar boost_fx: CPUParticles3D",
        1,
    )

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
    anchor2 = "func _tick_vehicle_visual(delta: float) -> void:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, builder + anchor2, 1)

# drive the exhaust from the vehicle tick
old = "\tif not is_instance_valid(vehicle_model): return"
new = '''	if not is_instance_valid(vehicle_model): return
	# Exhaust sits at the tail of the car and only fires while the run is moving fast.
	var vstat: Dictionary = VEHICLE_STATS.get(vehicle, {})
	var vfast: float = float(vstat.get("speed", 0.0))
	if vfast >= 3.4:
		_build_boost()
		if is_instance_valid(boost_fx):
			boost_fx.global_position = vehicle_model.global_position + Vector3(0, 0.45, 1.15)
			boost_fx.emitting = true
	elif is_instance_valid(boost_fx):
		boost_fx.emitting = false'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("vehicle exhaust added for fast vehicles")
