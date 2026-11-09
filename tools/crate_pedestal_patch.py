import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "const USE_AMMO_CAN" not in t:
    anchor = "const AMMO_CAN_PATH := \"res://assets/models/ammo_pickup.glb\""
    assert t.count(anchor) == 1
    t = t.replace(
        anchor,
        anchor + "\n## false = the crate sits on the green supply-truck pedestal again (user's call: the\n"
        "## ammo can had replaced that pedestal).",
        1,
    )
    t = t.replace(
        "## ammo can had replaced that pedestal).",
        "## ammo can had replaced that pedestal).\nconst USE_AMMO_CAN := false",
        1,
    )

old = "\tif ResourceLoader.exists(AMMO_CAN_PATH):"
assert t.count(old) == 1
t = t.replace(old, "\tif USE_AMMO_CAN and ResourceLoader.exists(AMMO_CAN_PATH):", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("green truck pedestal restored")
