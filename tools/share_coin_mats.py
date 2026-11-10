import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\pickup_3d.gd"
t = io.open(P, encoding="utf-8").read()

# shared per-colour materials: one duplicate per pickup meant one shader compile per pickup
if "_coin_mat_cache" not in t:
    anchor = "const GOLD_ALBEDO:=Color(1.0,0.80,0.32)"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## One material per coin colour, shared by every pickup: duplicating per instance\n## created hundreds of materials, and each new material compiles a shader.\nstatic var _coin_mat_cache:={}", 1)

old = '''		var mat: StandardMaterial3D=(src as StandardMaterial3D).duplicate() as StandardMaterial3D
		mat.albedo_color=albedo'''
new = '''		var key: int = albedo.to_rgba32()
		var mat: StandardMaterial3D = _coin_mat_cache.get(key, null) as StandardMaterial3D
		if mat == null:
			mat = (src as StandardMaterial3D).duplicate() as StandardMaterial3D
			mat.albedo_color = albedo
			_coin_mat_cache[key] = mat'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("coin materials are shared instead of duplicated per pickup")
