import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "USE_FULL_TRUCK" not in t:
    old = "const USE_AMMO_CAN := false"
    assert t.count(old) == 1
    t = t.replace(
        old,
        old
        + "\n## true = the whole supply truck stands on the road as the pedestal and the crate body\n"
        + "## sits on it, which is how the green boxes used to arrive.",
        1,
    )
    t = t.replace(
        "## sits on it, which is how the green boxes used to arrive.",
        "## sits on it, which is how the green boxes used to arrive.\nconst USE_FULL_TRUCK := true",
        1,
    )

old_branch = "\tif can_used:\n\t\tpass\n\telif crate_mesh:"
new_branch = '''	if can_used:
		pass
	elif USE_FULL_TRUCK and ResourceLoader.exists(TRUCK_PATH):
		# The truck is the pedestal: it is what the green crates rode in on. Normalise it by its
		# own bounds so it stays road-sized no matter how the GLB was authored.
		var truck := (load(TRUCK_PATH) as PackedScene).instantiate() as Node3D
		if truck != null:
			body.add_child(truck)
			var tspan := _bounds_of(truck)
			var tk := 3.10 / maxf(tspan.size.z, 0.01)
			truck.scale = Vector3.ONE * tk
			truck.position = Vector3(-tspan.get_center().x * tk, -tspan.position.y * tk, -tspan.get_center().z * tk)
	elif crate_mesh:'''
assert t.count(old_branch) == 1
t = t.replace(old_branch, new_branch, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("supply truck restored as the crate pedestal")
