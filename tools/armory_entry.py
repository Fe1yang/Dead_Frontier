import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# main: tapping the armory button inside the truck screen opens it
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''func _armory_pointer(pos: Vector2) -> bool:
	if state != "armory":
		return false'''
new = '''func _armory_pointer(pos: Vector2) -> bool:
	if state == "shop" and ARMORY_BTN.has_point(pos):
		open_armory()
		return true
	if state == "armory" and ARMORY_BACK.has_point(pos):
		close_armory()
		return true
	if state != "armory":
		return false'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

if "const ARMORY_BACK" not in t:
    t = t.replace(
        "const ARMORY_VIEW := Rect2(40, 158, 460, 380)",
        "const ARMORY_VIEW := Rect2(40, 158, 460, 380)\nconst ARMORY_BACK := Rect2(24, 24, 100, 48)\nconst ARMORY_PREV := Rect2(60, 736, 60, 44)\nconst ARMORY_NEXT := Rect2(420, 736, 60, 44)",
        1,
    )

# prev / next inside the armory
old_nav = '''	if state != "armory":
		return false
	if ARMORY_VIEW.has_point(pos):'''
new_nav = '''	if state != "armory":
		return false
	if ARMORY_PREV.has_point(pos):
		armory_step(-1)
		return true
	if ARMORY_NEXT.has_point(pos):
		armory_step(1)
		return true
	if ARMORY_VIEW.has_point(pos):'''
if t.count(old_nav) == 1:
    t = t.replace(old_nav, new_nav, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: armory button + nav taps")

# hud: draw the armory button on the truck screen
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()
old_btn = '\t_var_lang_none = 0'
anchor = '\t_button(Rect2(404,24,112,48),ShopText.text(lang,"cases"),true)'
assert h.count(anchor) == 1, h.count(anchor)
h = h.replace(anchor, anchor + '''
	# armory entry: a second button under the case button
	_box(game.ARMORY_BTN, Color(0.10, 0.11, 0.12, 0.95), Color(LINE, 1.0), 0)
	_text_center("军械库" if String(lang).begins_with("zh") else "ARMORY", game.ARMORY_BTN.get_center() + Vector2(0, 6), 16, WHITE)''', 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: armory button drawn")
