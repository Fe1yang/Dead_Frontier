import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) FUEL becomes a crate reward: it tops up whichever thing the player is using.
anchor = '\tif crate.weapon_id=="SEDAN":'
assert t.count(anchor) == 1
reward = '''	if crate.weapon_id=="FUEL":
		_refuel(); sound.play("gate")
		return
'''
t = t.replace(anchor, reward + anchor, 1)

# 2) the refuel helper: a fuel can is a reset, never a stack
anchor2 = "## Fallen bodies ride the scrolling road exactly like obstacles do"
assert t.count(anchor2) == 1
helper = '''## Fuel can: refills whatever is carrying the player. On a vehicle it resets the tank (so the
## remaining range becomes a full VEHICLE_AUTO_RANGE again, never stacked on top of it); on foot
## with the flamethrower it refills the fuel instead.
func _refuel() -> void:
	if player.vehicle != "":
		player.vehicle_durability = 100.0
		vehicle_range_end = distance + VEHICLE_AUTO_RANGE
		_popup(player.position+Vector3(0,2.5,0),"FUEL: FULL",Color("ffb14d"))
	elif player.weapon == "FLAME":
		player.ammo = player.magazine_size
		player.reserve_ammo = mini(player.reserve_ammo + 100, player.magazine_size * 3)
		_popup(player.position+Vector3(0,2.5,0),"FLAME FUEL +100",Color("ff9b35"))
	else:
		run_coins += 15
		_popup(player.position+Vector3(0,2.5,0),"+15",Color("ffd27a"))

''' + anchor2
t = t.replace(anchor2, helper, 1)

# 3) the vehicle range: a refuel must extend the end point, not restart the counter
if "var vehicle_range_end" not in t:
    t = t.replace(
        "var vehicle_auto_active:=false",
        "var vehicle_auto_active:=false\n## Distance at which the bought bike gives out; a fuel can pushes it out again.\nvar vehicle_range_end:=VEHICLE_AUTO_RANGE",
        1,
    )

t = t.replace(
    "\tif vehicle_auto_active and distance>=VEHICLE_AUTO_RANGE:",
    "\tif vehicle_auto_active and distance>=vehicle_range_end:",
    1,
)

if "vehicle_range_end=VEHICLE_AUTO_RANGE" not in t.split("func _refuel")[0].replace("var vehicle_range_end:=VEHICLE_AUTO_RANGE", ""):
    t = t.replace(
        "\tvehicle_auto_active=loadout_on and vehicle_equipped and owned_vehicle!=\"\"",
        "\tvehicle_range_end=VEHICLE_AUTO_RANGE\n\tvehicle_auto_active=loadout_on and vehicle_equipped and owned_vehicle!=\"\"",
        1,
    )

# 4) only offer fuel when it is useful: mounted, or on foot with the flamethrower
old_gear = '''		elif rng.randf()<GEAR_CRATE_CHANCE:'''
new_gear = '''		elif (player.vehicle!="" or player.weapon=="FLAME") and rng.randf()<FUEL_CRATE_CHANCE:
			id="FUEL"
		elif rng.randf()<GEAR_CRATE_CHANCE:'''
assert t.count(old_gear) == 1
t = t.replace(old_gear, new_gear, 1)

if "FUEL_CRATE_CHANCE" not in t.split("elif (player.vehicle")[0]:
    t = t.replace(
        "const GEAR_CRATE_CHANCE:=0.22",
        "const GEAR_CRATE_CHANCE:=0.22\nconst FUEL_CRATE_CHANCE:=0.30   # only while riding or holding the flamethrower",
        1,
    )

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("fuel can: crate drop, refuel helper, range end")
