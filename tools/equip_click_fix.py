import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if was_drag or not lobby_view_rect().has_point(pos): return
	if equip_menu_index>=0:
		if equip_menu_rect().has_point(pos):
			select_character(equip_menu_index); equip_menu_index=-1; return
		equip_menu_index=-1  # tapping elsewhere closes the dropdown'''

new = '''	if was_drag: return
	# The dropdown sits above the card strip, outside lobby_view_rect(), so it used to be rejected
	# by the guard below and every tap fell through to the card underneath.
	if equip_menu_index>=0:
		if equip_menu_rect().has_point(pos):
			select_character(equip_menu_index); equip_menu_index=-1; return
		equip_menu_index=-1  # tapping elsewhere closes the dropdown
	if not lobby_view_rect().has_point(pos): return'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("equip dropdown is now hit-tested before the card strip guard")
