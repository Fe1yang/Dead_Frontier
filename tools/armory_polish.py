import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) per-weapon size in the armory: the Makarov fills the frame, so it gets its own multiplier
if "const ARMORY_SIZE" not in t:
    t = t.replace(
        "const ARMORY_VIEW := Rect2(40, 158, 460, 380)",
        'const ARMORY_VIEW := Rect2(40, 158, 460, 380)\n'
        '## Per-weapon size multiplier for the armory stage (compact guns would fill the frame).\n'
        'const ARMORY_SIZE := {"MAKAROV": 0.66, "PISTOL": 0.86, "SUOMI": 1.0, "SMG": 1.0,\n'
        '\t"SHOTGUN": 1.0, "SNIPER": 1.0, "LAUNCHER": 1.0, "FLAME": 1.0}',
        1,
    )

old_k = "\tvar k := 0.62 / maxf(0.001, span)"
new_k = "\tvar k := 0.62 * float(ARMORY_SIZE.get(id, 1.0)) / maxf(0.001, span)"
assert t.count(old_k) == 1
t = t.replace(old_k, new_k, 1)

# 2) rotation around a dedicated pivot so both axes read as a free spin
old_drag = '''			armory_model.rotation.y -= event.relative.x * 0.012
			# vertical drag tilts it too, so every angle is reachable
			armory_model.rotation.x = clampf(armory_model.rotation.x - event.relative.y * 0.010, deg_to_rad(-70.0), deg_to_rad(70.0))'''
new_drag = '''			# spin around a pivot so horizontal drag is a yaw and vertical drag a pitch,
			# which lets every angle be reached
			armory_pivot.rotation.y -= event.relative.x * 0.012
			armory_pivot.rotation.x = clampf(armory_pivot.rotation.x - event.relative.y * 0.010, deg_to_rad(-85.0), deg_to_rad(85.0))'''
assert t.count(old_drag) == 1
t = t.replace(old_drag, new_drag, 1)

# the pivot itself
if "var armory_pivot" not in t:
    t = t.replace("var armory_model: Node3D", "var armory_pivot: Node3D\nvar armory_model: Node3D", 1)

old_add = "\tarmory_stage.add_child(model)\n\tarmory_model = model"
new_add = '''	if not is_instance_valid(armory_pivot):
		armory_pivot = Node3D.new()
		armory_stage.add_child(armory_pivot)
	armory_pivot.add_child(model)
	armory_pivot.rotation = Vector3.ZERO
	armory_model = model'''
assert t.count(old_add) == 1
t = t.replace(old_add, new_add, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("main: per-weapon size, pivot rotation")

# 3) the upgrade row shows for every gun, disabled when there is nothing to buy
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()
old_row = '''	if lv_max > 0:
		_text("升级  LV %d / %d" % [lv, lv_max], Vector2(60, 706), 15, GOLD)
		_button(game.ARMORY_UPGRADE, ("升级  %d 银币" % game.armory_price()) if lv < lv_max else "已满级", lv < lv_max)'''
new_row = '''	if lv_max > 0:
		_text("升级  LV %d / %d" % [lv, lv_max], Vector2(60, 706), 15, GOLD)
		_button(game.ARMORY_UPGRADE, ("升级  %d 银币" % game.armory_price()) if lv < lv_max else "已满级", lv < lv_max)
	else:
		_text("升级  此枪不可升级", Vector2(60, 706), 15, MUTED)
		_button(game.ARMORY_UPGRADE, "不可升级", false)'''
assert h.count(old_row) == 1
h = h.replace(old_row, new_row, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("hud: upgrade row always visible")
