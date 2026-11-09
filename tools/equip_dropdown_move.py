import io

mp = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(mp, encoding="utf-8").read()

old = '''	# Below the card, never above it: above the card sits the tab row, and the popup used to
	# cover the tab labels.
	return Rect2(c.position.x-6.0,c.position.y+c.size.y+8.0,c.size.x+12.0,54.0)'''
new = '''	# Above the card. Below it the popup landed on the start button and was unclickable.
	return Rect2(c.position.x-6.0,c.position.y-58.0,c.size.x+12.0,50.0)'''
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(mp, "w", encoding="utf-8", newline="\n").write(t)

hp = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(hp, encoding="utf-8").read()

# opaque panel: while the dropdown is open it must hide the tab labels behind it
old_panel = "\t\t_panel(er, Color(0.03,0.034,0.038,0.97), RED if equipped_now else Color(0.55,0.57,0.58,0.9), 1)"
new_panel = "\t\t_panel(er, Color(0.03,0.034,0.038,1.0), RED if equipped_now else Color(0.72,0.74,0.75,1.0), 2)"
assert h.count(old_panel) == 1
h = h.replace(old_panel, new_panel, 1)
io.open(hp, "w", encoding="utf-8", newline="\n").write(h)
print("equip dropdown moved above the card, opaque")
