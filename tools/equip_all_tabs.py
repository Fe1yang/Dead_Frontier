import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# ---------- main_3d ----------
p = base + r"\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "var equip_menu_tab:=" not in t:
    old = "var equip_menu_index:=-1  # survivor card whose EQUIP dropdown is open"
    new = ("var equip_menu_index:=-1  # card whose EQUIP dropdown is open\n"
           "var equip_menu_tab:=0     # ...and which tab it belongs to")
    assert t.count(old) == 1
    t = t.replace(old, new, 1)

old_confirm = '''	if equip_menu_index>=0:
		if equip_menu_rect().has_point(pos):
			select_character(equip_menu_index); equip_menu_index=-1; sound.play("equip"); return
		equip_menu_index=-1  # tapping elsewhere just closes the dropdown
		return              # and the tap goes no further'''
new_confirm = '''	if equip_menu_index>=0:
		if equip_menu_rect().has_point(pos):
			_equip_from_menu()
			equip_menu_index=-1; sound.play("equip"); return
		equip_menu_index=-1  # tapping elsewhere just closes the dropdown
		return              # and the tap goes no further'''
assert t.count(old_confirm) == 1
t = t.replace(old_confirm, new_confirm, 1)

# the equip action depends on the tab the dropdown was opened from
if "func _equip_from_menu()" not in t:
    helper = '''## Wears whatever the open dropdown points at, on whichever tab opened it.
func _equip_from_menu() -> void:
	match equip_menu_tab:
		1:
			if equip_menu_index < lobby.PETS.size():
				select_pet(equip_menu_index)
		2:
			if equip_menu_index < lobby.SKINS.size():
				select_skin(equip_menu_index)
		3:
			var vkey: String = String(["BIKE","SPORT","CRUISER","GOLD","TANK","SEDAN","GOLD_CAR"][clampi(equip_menu_index,0,6)])
			if vehicle_is_owned(String(["vehicle_bike","vehicle_sport","vehicle_car","vehicle_gold","vehicle_tank","vehicle_sedan","vehicle_gold_car"][clampi(equip_menu_index,0,6)])):
				owned_vehicle = vkey
				_save()
		_:
			select_character(equip_menu_index)


'''
    anchor = "func _lobby_release(pos: Vector2) -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

# vehicles / skins / pets: a first tap now opens the dropdown instead of equipping straight away
old_veh = '''				if vehicle_is_owned(String(["vehicle_bike","vehicle_sport","vehicle_car","vehicle_gold","vehicle_tank","vehicle_sedan","vehicle_gold_car"][clampi(i,0,6)])):
					owned_vehicle=vkey; _save(); sound.play("equip")'''
new_veh = '''				if vehicle_is_owned(String(["vehicle_bike","vehicle_sport","vehicle_car","vehicle_gold","vehicle_tank","vehicle_sedan","vehicle_gold_car"][clampi(i,0,6)])):
					if owned_vehicle == vkey:
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i; equip_menu_tab=3'''
assert t.count(old_veh) == 1, t.count(old_veh)
t = t.replace(old_veh, new_veh, 1)

old_skin = '''			elif lobby_tab==2:
				if i<lobby.SKINS.size(): select_skin(i)
				else: lobby_toast=1.6; lobby_toast_key="coming"'''
new_skin = '''			elif lobby_tab==2:
				if i<lobby.SKINS.size():
					if skin_choice == i and skin_equipped:
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i; equip_menu_tab=2
				else: lobby_toast=1.6; lobby_toast_key="coming"'''
assert t.count(old_skin) == 1
t = t.replace(old_skin, new_skin, 1)

old_pet = '''			elif lobby_tab==1:
				if i<lobby.PETS.size(): select_pet(i)
				else: lobby_toast=1.6; lobby_toast_key="coming"'''
new_pet = '''			elif lobby_tab==1:
				if i<lobby.PETS.size():
					if pet_choice == i and pet_equipped:
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i; equip_menu_tab=1
				else: lobby_toast=1.6; lobby_toast_key="coming"'''
assert t.count(old_pet) == 1
t = t.replace(old_pet, new_pet, 1)

# opening on the survivor tab records the tab too
t = t.replace("\t\t\t\t\t\tequip_menu_index=i\n", "\t\t\t\t\t\tequip_menu_index=i; equip_menu_tab=0\n", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main_3d: equip dropdown on pets, skins and vehicles too")

# ---------- hud ----------
hp = base + r"\hud.gd"
h = io.open(hp, encoding="utf-8").read()

h = h.replace('if game.lobby_tab==0 and int(game.equip_menu_index)>=0:',
              'if int(game.equip_menu_index)>=0:', 1)
h = h.replace('var equipped_now: bool = int(game.equip_menu_index) == game.character_choice',
              'var equipped_now: bool = int(game.equip_menu_index) == (game.character_choice if int(game.equip_menu_tab)==0 else -1)', 1)
h = h.replace('var menu_open: bool = game.lobby_tab==0 and int(game.equip_menu_index)==i',
              'var menu_open: bool = int(game.equip_menu_index)==i', 1)

io.open(hp, "w", encoding="utf-8", newline="\n").write(h)
print("hud: dropdown draws on every tab")
