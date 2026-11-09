import io

HP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
MP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"

h = io.open(HP, encoding="utf-8").read()
old = '\tvar etxt: String="装备" if String(game.language_code).begins_with("zh") else "EQUIP"'
new = (
    '\tvar zh: bool=String(game.language_code).begins_with("zh")\n'
    '\tvar etxt: String=("已装备" if zh else "EQUIPPED") if equipped_now else ("装备" if zh else "EQUIP")'
)
assert h.count(old) == 1
h = h.replace(old, new, 1)
io.open(HP, "w", encoding="utf-8", newline="\n").write(h)

t = io.open(MP, encoding="utf-8").read()
# never offer the dropdown for something that is not owned
old_open = '''			elif i<lobby.CHARACTERS.size():
				# preview the survivor and offer the dropdown; wearing them is a second tap
				if character_owned(i):
					equip_menu_index=i
					lobby.show_character(i,character_asset(i))
				else: select_character(i)'''
new_open = '''			elif i<lobby.CHARACTERS.size():
				# preview the survivor and offer the dropdown; wearing them is a second tap
				if character_owned(i):
					lobby.show_character(i,character_asset(i))
					if i==character_choice:
						# already worn: no dropdown, just say so
						lobby_toast=1.6; lobby_toast_key="char_equipped"
					else:
						equip_menu_index=i
				else: select_character(i)'''
assert t.count(old_open) == 1
t = t.replace(old_open, new_open, 1)
io.open(MP, "w", encoding="utf-8", newline="\n").write(t)
print("dropdown shows EQUIPPED and never opens for locked or already-worn survivors")
