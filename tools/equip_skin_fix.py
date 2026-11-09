import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''				if i<lobby.SKINS.size():
					if skin_choice == i and skin_equipped:
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i; equip_menu_tab=2'''
new = '''				if i<lobby.SKINS.size():
					if int(skin_choice.get(character_choice, -1)) == i:
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i; equip_menu_tab=2'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("skin comparison fixed")
