import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# use the Wallcoeur flame sprite instead of the old hand-made particle
old_tex = 'mat.albedo_texture = load("res://assets/vfx/flame_particle.png")'
new_tex = 'mat.albedo_texture = load("res://assets/vfx/flame_soft.png")'
assert t.count(old_tex) == 1
t = t.replace(old_tex, new_tex, 1)

# a second, slower smoke layer on top of the fire reads as a real flame plume
anchor = "\tjet.emitting = false\n\tadd_child(jet)\n\tflame_jet = jet"
assert t.count(anchor) == 1
smoke = '''	jet.emitting = false
	add_child(jet)
	flame_jet = jet
	var smoke := CPUParticles3D.new()
	smoke.amount = 70
	smoke.lifetime = 1.05
	smoke.preprocess = 0.1
	smoke.local_coords = false
	smoke.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	smoke.emission_sphere_radius = 0.09
	smoke.direction = Vector3(0, 0, -1)
	smoke.spread = 12.0
	smoke.gravity = Vector3(0, 1.9, 0)
	smoke.initial_velocity_min = 4.0
	smoke.initial_velocity_max = 7.0
	smoke.scale_amount_min = 0.7
	smoke.scale_amount_max = 1.9
	var smoke_ramp := Gradient.new()
	smoke_ramp.set_color(0, Color(0.35, 0.32, 0.30, 0.0))
	smoke_ramp.add_point(0.15, Color(0.42, 0.38, 0.35, 0.5))
	smoke_ramp.add_point(0.6, Color(0.25, 0.23, 0.22, 0.28))
	smoke_ramp.set_color(3, Color(0.15, 0.14, 0.14, 0.0))
	smoke.color_ramp = smoke_ramp
	var squad := QuadMesh.new()
	squad.size = Vector2(0.75, 0.75)
	var smat := StandardMaterial3D.new()
	smat.albedo_texture = load("res://assets/vfx/smoke_soft.png")
	smat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	smat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	smat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	smat.vertex_color_use_as_albedo = true
	squad.material = smat
	smoke.mesh = squad
	smoke.emitting = false
	add_child(smoke)
	flame_smoke = smoke'''
t = t.replace(anchor, smoke, 1)

if "var flame_smoke" not in t:
    t = t.replace("var flame_glow: OmniLight3D", "var flame_glow: OmniLight3D\nvar flame_smoke: CPUParticles3D", 1)

# keep the smoke in step with the fire
old_on = "\tif is_instance_valid(flame_glow):\n\t\tflame_glow.light_energy = 1.5"
if t.count(old_on) == 0:
    old_on = "\tif is_instance_valid(flame_glow):\n\t\tflame_glow.light_energy = 0.35"
assert t.count(old_on) == 1, t.count(old_on)
t = t.replace(old_on, old_on + "\n\tif is_instance_valid(flame_smoke):\n\t\tflame_smoke.emitting = true\n\t\tflame_smoke.global_position = flame_jet.global_position\n\t\tflame_smoke.look_at(flame_jet.global_position + (flame_jet.global_transform.basis.z * -1.0) * 6.0, Vector3.UP)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame jet uses the Wallcoeur sprite plus a smoke layer")
