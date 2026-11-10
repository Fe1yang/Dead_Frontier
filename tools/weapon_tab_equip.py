import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# ---- weapons tab: an EQUIP button, never a jump into the store ----
old = '''			if lobby_tab==4:
				open_store()
				return'''
new = '''			if lobby_tab==4:
				# one card: the flamethrower. Owned ones offer EQUIP, unowned ones just say so.
				if not flame_owned():
					lobby_toast=1.8; lobby_toast_key="char_locked"
				elif flame_equipped:
					lobby_toast=1.6; lobby_toast_key="char_equipped"
				else:
					equip_menu_index=i; equip_menu_tab=4
				return'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# the equip action for that tab
old_match = '''		3:
			var vkey: String = String(["BIKE","SPORT","CRUISER","GOLD","TANK","SEDAN","GOLD_CAR"][clampi(equip_menu_index,0,6)])'''
new_match = '''		3:
			var vkey: String = String(["BIKE","SPORT","CRUISER","GOLD","TANK","SEDAN","GOLD_CAR"][clampi(equip_menu_index,0,6)])'''
assert t.count(old_match) == 1

if "4:\n\t\t\tflame_equipped" not in t:
    anchor = '''		_:
			select_character(equip_menu_index)'''
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''		4:
			flame_equipped = true
			_save()
		_:
			select_character(equip_menu_index)''', 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("weapons tab opens the equip dropdown instead of the store")
