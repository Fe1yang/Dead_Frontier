import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "USE_AMMO_CAN" not in t:
    old = 'const AMMO_CAN_PATH := "res://assets/models/ammo_pickup.glb"'
    assert t.count(old) == 1
    t = t.replace(
        old,
        old
        + "\n## false = the crate sits on the green supply-truck pedestal again; the ammo can had\n"
        + "## replaced that pedestal and the user wants the green base back.\n"
        + "const USE_AMMO_CAN := false",
        1,
    )

old = "\tif ResourceLoader.exists(AMMO_CAN_PATH):"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, "\tif USE_AMMO_CAN and ResourceLoader.exists(AMMO_CAN_PATH):", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("green truck pedestal restored")
