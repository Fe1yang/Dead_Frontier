import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

# An unknown or missing model left the barrel/crate completely bare, which reads as a bug in the
# run. Show a small glowing marker instead so the drop is always visible.
old = '''		if packed_model==null:
			push_error("crate: missing model for "+String(weapon_id)+" -> "+path)
			return'''
new = '''		if packed_model==null:
			push_error("crate: missing model for "+String(weapon_id)+" -> "+path)
			weapon_model = _fallback_marker()
			weapon_pivot.add_child(weapon_model)
			return'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# also cover the case where the file simply does not exist
old2 = "\tif path!=\"\" and ResourceLoader.exists(path):"
new2 = "\tif path!=\"\" and not ResourceLoader.exists(path):\n\t\tweapon_model = _fallback_marker()\n\t\tweapon_pivot.add_child(weapon_model)\n\t\tpath = \"\"\n\tif path!=\"\" and ResourceLoader.exists(path):"
assert t.count(old2) == 1
t = t.replace(old2, new2, 1)

helper = '''## Something visible for a drop whose model is missing: a small glowing diamond.
func _fallback_marker() -> Node3D:
	var mi := MeshInstance3D.new()
	var mesh := SphereMesh.new()
	mesh.radius = 0.18
	mesh.height = 0.36
	mesh.radial_segments = 8
	mesh.rings = 4
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(0.45, 0.85, 1.0, 0.9)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mesh.material = mat
	mi.mesh = mesh
	return mi


'''
anchor = "func _model_span(node: Node3D) -> float:"
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("missing drop models now show a marker instead of nothing")
