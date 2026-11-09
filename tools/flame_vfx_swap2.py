import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# swap the sprite the jet uses (there is also an unrelated material at line ~450; only the jet one
# sits inside _build_flame_jet)
start = t.find("func _build_flame_jet() -> void:")
end = t.find("func pulse_flame() -> void:")
assert start > 0 and end > start
body = t[start:end]

old_tex = 'load("res://assets/vfx/flame_particle.png")'
assert body.count(old_tex) == 1, body.count(old_tex)
body = body.replace(old_tex, 'load("res://assets/vfx/flame_soft.png")', 1)

anchor = "\tjet.emitting = false\n\tadd_child(jet)\n\tflame_jet = jet"
assert body.count(anchor) == 1, body.count(anchor)
smoke = '''	jet.emitting = false
	add_child(jet)
	flame_jet = jet
	# a slower smoke layer over the fire reads as a real plume
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
body = body.replace(anchor, smoke, 1)
t = t[:start] + body + t[end:]

if "var flame_smoke" not in t:
    t = t.replace("var flame_glow: OmniLight3D", "var flame_glow: OmniLight3D\nvar flame_smoke: CPUParticles3D", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame sprite swapped + smoke layer added")
