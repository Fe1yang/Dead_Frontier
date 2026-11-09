import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

start = t.find("func _build_flame_jet() -> void:")
end = t.find("func pulse_flame() -> void:")
assert start > 0 and end > start

new_builder = '''func _build_flame_jet() -> void:
	if is_instance_valid(flame_jet):
		return
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1.0, 1.0, 0.92, 0.0))
	ramp.add_point(0.06, Color(1.0, 1.0, 0.85, 1.0))
	ramp.add_point(0.22, Color(1.0, 0.86, 0.35, 0.98))
	ramp.add_point(0.45, Color(1.0, 0.52, 0.10, 0.90))
	ramp.add_point(0.72, Color(0.78, 0.18, 0.04, 0.45))
	ramp.set_color(3, Color(0.12, 0.09, 0.08, 0.0))
	var jet := CPUParticles3D.new()
	jet.amount = 240
	jet.lifetime = 0.85
	jet.preprocess = 0.12
	jet.local_coords = false
	jet.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	jet.emission_sphere_radius = 0.07
	jet.direction = Vector3(0, 0, -1)
	jet.spread = 9.0
	jet.gravity = Vector3(0, 2.2, 0)
	jet.initial_velocity_min = 14.0
	jet.initial_velocity_max = 22.0
	jet.angular_velocity_min = -60.0
	jet.angular_velocity_max = 60.0
	jet.scale_amount_min = 0.85
	jet.scale_amount_max = 2.3
	# flame grows as it leaves the nozzle, then thins out while it cools
	var grow := Curve.new()
	grow.add_point(Vector2(0.0, 0.35))
	grow.add_point(Vector2(0.35, 1.0))
	grow.add_point(Vector2(1.0, 1.35))
	jet.scale_amount_curve = grow
	jet.color_ramp = ramp
	var quad := QuadMesh.new()
	quad.size = Vector2(0.85, 0.85)
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = load("res://assets/vfx/flame_particle.png")
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.vertex_color_use_as_albedo = true
	mat.no_depth_test = false
	quad.material = mat
	jet.mesh = quad
	jet.emitting = false
	add_child(jet)
	flame_jet = jet
	# the jet lights the street in front of the survivor
	var glow := OmniLight3D.new()
	glow.light_color = Color("ff8a3c")
	glow.omni_range = 7.5
	glow.light_energy = 0.0
	glow.shadow_enabled = false
	jet.add_child(glow)
	flame_glow = glow


'''

t = t[:start] + new_builder + t[end:]

if "var flame_glow" not in t:
    t = t.replace(
        "var flame_jet: CPUParticles3D",
        "var flame_jet: CPUParticles3D\nvar flame_glow: OmniLight3D",
        1,
    )

# keep the glow alive while the jet burns
old_pulse = '''	flame_jet_timer = 0.18
	flame_jet.emitting = true'''
new_pulse = '''	flame_jet_timer = 0.20
	flame_jet.emitting = true
	if is_instance_valid(flame_glow):
		flame_glow.light_energy = 3.4'''
assert t.count(old_pulse) == 1
t = t.replace(old_pulse, new_pulse, 1)

old_stop = '''		if flame_jet_timer <= 0.0:
			flame_jet.emitting = false'''
new_stop = '''		if flame_jet_timer <= 0.0:
			flame_jet.emitting = false
			if is_instance_valid(flame_glow):
				flame_glow.light_energy = 0.0'''
assert t.count(old_stop) == 1
t = t.replace(old_stop, new_stop, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame jet rebuilt: 240 particles, growth curve, additive, muzzle light")
