import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# ---------------- hud: draw the gear toggle for every tab that has one ----------------
p = ROOT + r"\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

anchor = '''	# Perk tag for the selected survivor, right of the tabs (only Darius has one for now).'''
assert h.count(anchor) == 1
gear = '''	# Equip toggle per tab: survivor loadout, pet and vehicle each get their own switch.
	if game.lobby_tab==0:
		_gear_button(game.LOBBY_GEAR, game.loadout_on)
	elif game.lobby_tab==1:
		_gear_button(game.LOBBY_GEAR_PET, game.pet_equipped)
	elif game.lobby_tab==3:
		_gear_button(game.LOBBY_GEAR_VEHICLE, game.vehicle_equipped)
''' + anchor
h = h.replace(anchor, gear, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("hud: gear buttons drawn for survivor / pet / vehicle tabs")

# ---------------- main: taps on those switches ----------------
p2 = ROOT + r"\scripts\main_3d.gd"
t = io.open(p2, encoding="utf-8").read()

if "func _lobby_gear_pointer" not in t:
    anchor2 = "func _armory_pointer(pos: Vector2) -> bool:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, '''## Equip switches in the lobby: one per tab, routed through a small standalone handler so the
## long pointer chain below stays untouched.
func _lobby_gear_pointer(pos: Vector2) -> bool:
	if state != "lobby":
		return false
	if lobby_tab == 0 and LOBBY_GEAR.has_point(pos):
		toggle_loadout(); return true
	if lobby_tab == 1 and LOBBY_GEAR_PET.has_point(pos):
		toggle_pet_equip(); return true
	if lobby_tab == 3 and LOBBY_GEAR_VEHICLE.has_point(pos):
		toggle_vehicle_equip(); return true
	return false


''' + anchor2, 1)

old_call = "\tif _armory_pointer(pos): return true"
assert t.count(old_call) == 1
t = t.replace(old_call, "\tif _lobby_gear_pointer(pos): return true\n" + old_call, 1)

io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
print("main: gear taps wired")
