import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\effect_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "_static_cache" not in t:
    anchor = "func make_spark("
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''## Shared materials for sparks and droplets, keyed by mode and colour: these modes only change
## scale after setup, so one material per colour is safe and saves a shader compile each.
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

BLOCK = '''		effect_material=StandardMaterial3D.new(); effect_material.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		n.material_override=effect_material; add_child(n); visual=n
	effect_material.albedo_color=color'''

def patch_function(src, func_name, next_func, key):
    start = src.find("func %s(" % func_name)
    end = src.find("func %s(" % next_func, start)
    assert 0 < start < end, func_name
    body = src[start:end]
    assert BLOCK in body, func_name
    body = body.replace(BLOCK, '''		effect_material=_shared_material("%s", color)
		n.material_override=effect_material; add_child(n); visual=n''' % key, 1)
    return src[:start] + body + src[end:]

t = patch_function(t, "make_spark", "make_drop", "spark")
t = patch_function(t, "make_drop", "make_shockwave", "drop")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("spark and droplet materials are shared per colour")
