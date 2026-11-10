import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\effect_3d.gd"
t = io.open(P, encoding="utf-8").read()

# Sparks and droplets only ever change their scale after creation, so their material can be
# shared per colour. Blast / smoke / shockwave fade through albedo.a, so those stay per instance.
if "_static_cache" not in t:
    anchor = "func make_spark("
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''## Shared materials for sparks and droplets, keyed by mode and colour. These modes never touch
## the colour again after setup, only the scale, so one material per colour is safe.
static var _static_cache:={}


func _shared_material(mode_key: String, color: Color) -> StandardMaterial3D:
	var key: String = "%s|%d" % [mode_key, color.to_rgba32()]
	var mat: StandardMaterial3D = _static_cache.get(key, null) as StandardMaterial3D
	if mat == null:
		mat = StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.albedo_color = color
		_static_cache[key] = mat
	return mat


''' + anchor, 1)

# spark
old_spark = '''		effect_material=StandardMaterial3D.new(); effect_material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		n.material_override=effect_material; add_child(n); visual=n
	effect_material.albedo_color=color'''
new_spark = '''		effect_material=_shared_material("spark", color)
		n.material_override=effect_material; add_child(n); visual=n'''
assert t.count(old_spark) == 1, t.count(old_spark)
t = t.replace(old_spark, new_spark, 1)

# drop
old_drop = '''		effect_material=StandardMaterial3D.new(); effect_material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		n.material_override=effect_material; add_child(n); visual=n
	effect_material.albedo_color=color
	if velocity.length()>0.01:'''
new_drop = '''		effect_material=_shared_material("drop", color)
		n.material_override=effect_material; add_child(n); visual=n
	if velocity.length()>0.01:'''
assert t.count(old_drop) == 1, t.count(old_drop)
t = t.replace(old_drop, new_drop, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("spark and droplet materials are shared per colour")
