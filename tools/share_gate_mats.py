import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\gate_3d.gd"
t = io.open(P, encoding="utf-8").read()

# Gates are pooled and rebuilt often; every rebuild used to allocate a fresh material per post and
# per option, and each new material costs a shader compile in the Compatibility renderer.
if "_shared" not in t:
    anchor = "func _unshaded(color: Color,add:=false) -> StandardMaterial3D:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''## Materials are shared by colour and blend: the gate's look never changes at runtime.
static var _shared:={}


''' + anchor, 1)

old_unshaded = '''func _unshaded(color: Color,add:=false) -> StandardMaterial3D:
	var m:=StandardMaterial3D.new(); m.albedo_color=color
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode=BaseMaterial3D.CULL_DISABLED
	if add: m.blend_mode=BaseMaterial3D.BLEND_MODE_ADD
	return m'''
new_unshaded = '''func _unshaded(color: Color,add:=false) -> StandardMaterial3D:
	var key := "u|%d|%s" % [color.to_rgba32(), str(add)]
	var cached: StandardMaterial3D = _shared.get(key, null) as StandardMaterial3D
	if cached != null:
		return cached
	var m:=StandardMaterial3D.new(); m.albedo_color=color
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode=BaseMaterial3D.CULL_DISABLED
	if add: m.blend_mode=BaseMaterial3D.BLEND_MODE_ADD
	_shared[key] = m
	return m'''
assert t.count(old_unshaded) == 1, t.count(old_unshaded)
t = t.replace(old_unshaded, new_unshaded, 1)

old_post = '''	var post_mat:=StandardMaterial3D.new(); post_mat.albedo_color=Color("2f3436"); post_mat.roughness=0.5; post_mat.metallic=0.5'''
new_post = '''	var post_mat: StandardMaterial3D = _shared.get("post", null) as StandardMaterial3D
	if post_mat == null:
		post_mat = StandardMaterial3D.new()
		post_mat.albedo_color = Color("2f3436"); post_mat.roughness = 0.5; post_mat.metallic = 0.5
		_shared["post"] = post_mat'''
assert t.count(old_post) == 1, t.count(old_post)
t = t.replace(old_post, new_post, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("gate materials are shared by colour")
