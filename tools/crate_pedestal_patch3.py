import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# line 74 (index 73) is the CASE build; line 94 is the fallback lid path, which must keep working
if "USE_AMMO_CAN" not in "\n".join(lines):
    idx = next(i for i, l in enumerate(lines) if l.startswith('const AMMO_CAN_PATH'))
    lines[idx + 1:idx + 1] = [
        "## false = the crate sits on the green supply-truck pedestal again; the ammo can used to",
        "## replace that pedestal and the user wants the green base back.",
        "const USE_AMMO_CAN := false",
    ]

idx = next(i for i, l in enumerate(lines) if l == "\tif ResourceLoader.exists(AMMO_CAN_PATH):")
lines[idx] = "\tif USE_AMMO_CAN and ResourceLoader.exists(AMMO_CAN_PATH):"

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("green truck pedestal restored (case build only)")
