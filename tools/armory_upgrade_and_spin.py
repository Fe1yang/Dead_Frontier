import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) free rotation: vertical drag tilts the model as well
old = '''		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			return'''
new = '''		if event is InputEventScreenDrag or (event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT)):
			armory_model.rotation.y -= event.relative.x * 0.012
			# vertical drag tilts it too, so every angle is reachable
			armory_model.rotation.x = clampf(armory_model.rotation.x - event.relative.y * 0.010, deg_to_rad(-70.0), deg_to_rad(70.0))
			return'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# 2) upgrades happen here: the armory knows the shop id and the level
if "func armory_shop_id" not in t:
    anchor = "func armory_weapon_id() -> String:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''## The supply-shop item that upgrades this weapon ("" when the gun is not sold there).
func armory_shop_id() -> String:
	var id: String = armory_weapon_id().to_lower()
	var candidate := "w_" + id
	for item in shop_items:
		if String(item.id) == candidate:
			return candidate
	return ""


func armory_level() -> int:
	var sid := armory_shop_id()
	if sid == "":
		return 0
	return int(meta_upgrades.get(sid, 0))


func armory_max_level() -> int:
	var sid := armory_shop_id()
	if sid == "":
		return 0
	for item in shop_items:
		if String(item.id) == sid:
			return int(item.max_level)
	return 0


func armory_upgrade() -> void:
	var sid := armory_shop_id()
	if sid == "":
		return
	if buy_item(sid):
		_armory_show_weapon()


''' + anchor, 1)

# tap the upgrade button
old_nav = '''	if ARMORY_PREV.has_point(pos):'''
new_nav = '''	if ARMORY_UPGRADE.has_point(pos):
		armory_upgrade()
		return true
	if ARMORY_PREV.has_point(pos):'''
if t.count(old_nav) == 1:
    t = t.replace(old_nav, new_nav, 1)

t = t.replace(
    "const ARMORY_PREV := Rect2(60, 736, 60, 44)",
    "const ARMORY_PREV := Rect2(60, 736, 60, 44)\nconst ARMORY_UPGRADE := Rect2(150, 728, 240, 56)",
    1,
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: free rotation + armory upgrade")

# 3) hud: level row and the upgrade button
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()

old_rows = '''	# nav
	_box(Rect2(60, 736, 60, 44), Color(0.10, 0.11, 0.12, 1.0), Color(LINE, 1.0), 0)'''
new_rows = '''	# upgrade lives here now: level of this weapon plus the buy button
	var lv: int = game.armory_level()
	var lv_max: int = game.armory_max_level()
	if lv_max > 0:
		_text("升级  LV %d / %d" % [lv, lv_max], Vector2(60, 706), 15, GOLD)
		_button(game.ARMORY_UPGRADE, ("升级  %d 银币" % game.armory_price()) if lv < lv_max else "已满级", lv < lv_max)
	# nav
	_box(Rect2(60, 736, 60, 44), Color(0.10, 0.11, 0.12, 1.0), Color(LINE, 1.0), 0)'''
assert h.count(old_rows) == 1
h = h.replace(old_rows, new_rows, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: armory upgrade row")
