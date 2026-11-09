import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

# the truck brings a merchant NPC with it; the drop belongs on a raised platform instead
t = t.replace("const USE_FULL_TRUCK := true", "const USE_FULL_TRUCK := false", 1)

if "const PLATFORM_H" not in t:
    old = "const CRATE_SCALE := 2.9"
    assert t.count(old) == 1
    t = t.replace(
        old,
        old
        + "\n## Height of the concrete platform the drop stands on (the two platforms the crates\n"
        + "## have always been placed on, left and right of the lane).\n"
        + "const PLATFORM_H := 0.42",
        1,
    )

# build the platform and lift the crate onto it
old_tail = "\tweapon_pivot = Node3D.new(); weapon_pivot.position = Vector3(0,1.85,0); add_child(weapon_pivot)"
assert t.count(old_tail) == 1
new_tail = '''	# The drop stands on a platform, not on the road: a concrete slab with a steel edge.
	var plat := MeshInstance3D.new()
	var pbox := BoxMesh.new()
	pbox.size = Vector3(2.30, PLATFORM_H, 2.10)
	plat.mesh = pbox
	var pmat := StandardMaterial3D.new()
	pmat.albedo_color = Color("6d6f68")
	pmat.roughness = 0.92
	plat.material_override = pmat
	plat.position = Vector3(0, PLATFORM_H * 0.5, 0)
	add_child(plat)
	var trim := MeshInstance3D.new()
	var tbox := BoxMesh.new()
	tbox.size = Vector3(2.42, 0.07, 2.22)
	trim.mesh = tbox
	var tmat := StandardMaterial3D.new()
	tmat.albedo_color = Color("2f3335")
	tmat.roughness = 0.65
	trim.material_override = tmat
	trim.position = Vector3(0, PLATFORM_H, 0)
	add_child(trim)
	body.position.y = PLATFORM_H

''' + old_tail.replace("1.85,0", "1.85 + PLATFORM_H,0")
t = t.replace(old_tail, new_tail, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate now stands on a concrete platform; truck and its merchant are gone")
