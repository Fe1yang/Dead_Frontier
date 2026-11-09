import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# state for the weapon tab switch
if "var weapon_equipped" not in t:
    t = t.replace("var vehicle_equipped:=true", "var vehicle_equipped:=true\n## Whether the owned special weapon (the flamethrower) is carried into a run.\nvar weapon_equipped:=true", 1)

# honour it when the run starts
old_start = '''	if flame_owned():
		player.set_weapon("FLAME")'''
new_start = '''	if flame_owned() and weapon_equipped:
		player.set_weapon("FLAME")'''
assert t.count(old_start) == 1, t.count(old_start)
t = t.replace(old_start, new_start, 1)

# toggle + tap routing
if "func toggle_weapon_equip" not in t:
    anchor = "func _lobby_gear_pointer(pos: Vector2) -> bool:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''func toggle_weapon_equip() -> void:
	weapon_equipped = not weapon_equipped
	_save()
	lobby_toast = 1.4
	lobby_toast_key = "weapon_on" if weapon_equipped else "weapon_off"


''' + anchor, 1)

old_tap = '''	if lobby_tab == 3 and LOBBY_GEAR_VEHICLE.has_point(pos):
		toggle_vehicle_equip(); return true'''
new_tap = '''	if lobby_tab == 3 and LOBBY_GEAR_VEHICLE.has_point(pos):
		toggle_vehicle_equip(); return true
	if lobby_tab == 4 and LOBBY_GEAR.has_point(pos):
		toggle_weapon_equip(); return true'''
assert t.count(old_tap) == 1
t = t.replace(old_tap, new_tap, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: weapon equip switch")

# hud: draw it on the weapons tab
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()
old = '''	elif game.lobby_tab==3:
		_gear_button(game.LOBBY_GEAR_VEHICLE, game.vehicle_equipped)'''
new = '''	elif game.lobby_tab==3:
		_gear_button(game.LOBBY_GEAR_VEHICLE, game.vehicle_equipped)
	elif game.lobby_tab==4:
		_gear_button(game.LOBBY_GEAR, game.weapon_equipped)'''
assert h.count(old) == 1
h = h.replace(old, new, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: weapon gear button")
