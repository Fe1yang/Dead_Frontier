import io

MP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
HP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"

m = io.open(MP, encoding="utf-8").read()

# the top-right corner is the settings gear again; the ON/OFF loadout switch moves off it
old = '''	if lobby_tab == 0 and LOBBY_GEAR.has_point(pos):
		toggle_loadout(); return true'''
new = '''	if LOBBY_GEAR.has_point(pos):
		# top-right corner is the settings gear, as on every other screen
		settings_return_state = "character_select"; state = "settings"; return true'''
assert m.count(old) == 1, m.count(old)
m = m.replace(old, new, 1)

old4 = '''	if lobby_tab == 4 and LOBBY_GEAR.has_point(pos):
		toggle_weapon_equip(); return true'''
assert m.count(old4) == 1
m = m.replace(old4, '', 1)

io.open(MP, "w", encoding="utf-8", newline="\n").write(m)
print("gear pointer opens settings")

h = io.open(HP, encoding="utf-8").read()

# draw a gear instead of the ON/OFF plate in the top-right corner
old_draw = '''	_gear_button(game.LOBBY_GEAR, game.loadout_on)'''
new_draw = '''	_lobby_settings_gear(game.LOBBY_GEAR)'''
assert h.count(old_draw) == 1, h.count(old_draw)
h = h.replace(old_draw, new_draw, 1)

old_w = '''	_gear_button(game.LOBBY_GEAR, game.weapon_equipped)'''
assert h.count(old_w) == 1
h = h.replace(old_w, '', 1)

if "func _lobby_settings_gear" not in h:
    anchor = "func _gear_button(r: Rect2,on: bool) -> void:"
    assert h.count(anchor) == 1
    helper = '''## Settings gear in the lobby's top-right corner: same place and look as the in-run pause area.
func _lobby_settings_gear(r: Rect2) -> void:
	_panel(r, Color(0.06,0.07,0.075,0.92), Color(0.55,0.57,0.58,0.9), 1)
	_gear_icon(r.get_center(), r.size.y * 0.26, Color(0.86,0.87,0.88))


'''
    h = h.replace(anchor, helper + anchor, 1)

io.open(HP, "w", encoding="utf-8", newline="\n").write(h)
print("gear icon drawn in the top-right")
