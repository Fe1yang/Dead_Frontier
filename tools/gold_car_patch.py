import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '\t"GOLD_CAR": {"speed": 4.3, "side": 1.62, "ram": 3.4},'
new = '\t"GOLD_CAR": {"speed": 10.75, "side": 1.62, "ram": 3.4},   # +150% over the old 4.3'
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)

m = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
s = io.open(m, encoding="utf-8").read()

old2 = "\tvehicle_range_end=VEHICLE_AUTO_RANGE\n\tvehicle_auto_active=loadout_on and vehicle_equipped and owned_vehicle!=\"\""
new2 = (
    "\t# The gold sports car opens with a 2000 m dash; every other vehicle keeps 1000 m.\n"
    "\tvehicle_range_end=2000.0 if owned_vehicle==\"GOLD_CAR\" else VEHICLE_AUTO_RANGE\n"
    "\tvehicle_auto_active=loadout_on and vehicle_equipped and owned_vehicle!=\"\""
)
assert s.count(old2) == 1, s.count(old2)
s = s.replace(old2, new2, 1)
io.open(m, "w", encoding="utf-8", newline="\n").write(s)
print("gold car: speed 10.75 (+150%), opening dash 2000 m")
