import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

start = t.index("\tif can_used:")
end = t.index("\tvar band := MeshInstance3D.new()")
original = '''	if can_used:
		pass
	elif crate_mesh:
		# Exactly the build-3 rig: the green case itself is the platform, at CRATE_SCALE.
		var c := MeshInstance3D.new(); c.mesh = crate_mesh; c.scale = Vector3.ONE*s
		c.position = Vector3(0,0.15*s,0); body.add_child(c)
		if latch_mesh:
			var l := MeshInstance3D.new(); l.mesh = latch_mesh; l.scale = Vector3.ONE*s
			l.position = Vector3(0,0.15*s,0.22*s); body.add_child(l)
	else:
		var can_height := 0.78
'''
t = t[:start] + original + t[end:]

# drop the platform slab and the body lift added earlier
plat_start = t.find("\t# The drop stands on a platform, not on the road: a concrete slab with a steel edge.")
if plat_start != -1:
    plat_end = t.find("\tweapon_pivot = Node3D.new()", plat_start)
    t = t[:plat_start] + t[plat_end:]

t = t.replace("\tweapon_pivot = Node3D.new(); weapon_pivot.position = Vector3(0,1.85 + PLATFORM_H,0); add_child(weapon_pivot)",
              "\tweapon_pivot = Node3D.new(); weapon_pivot.position = Vector3(0,1.85,0); add_child(weapon_pivot)", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate restored to the build-3 rig (green case as the platform)")
