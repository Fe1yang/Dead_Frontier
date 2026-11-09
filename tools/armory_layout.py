import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

# lift the stat rows so the upgrade row has its own space, then place it below them
h = h.replace("\tvar y: float = 640.0", "\tvar y: float = 596.0", 1)
h = h.replace('_text("升级  LV %d / %d" % [lv, lv_max], Vector2(60, 706), 15, GOLD)',
              '_text("升级  LV %d / %d" % [lv, lv_max], Vector2(60, 706), 15, GOLD)', 1)
h = h.replace('_text("升级  此枪不可升级", Vector2(60, 706), 15, MUTED)',
              '_text("升级  此枪不可升级", Vector2(60, 706), 15, MUTED)', 1)

# buttons: upgrade at 716..768, nav at 786..830
h = h.replace('const ARMORY_UPGRADE := Rect2(150, 728, 240, 56)', 'const ARMORY_UPGRADE := Rect2(150, 716, 240, 52)')

io.open(p, "w", encoding="utf-8", newline="\n").write(h)

p2 = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p2, encoding="utf-8").read()
t = t.replace("const ARMORY_UPGRADE := Rect2(150, 728, 240, 56)", "const ARMORY_UPGRADE := Rect2(150, 716, 240, 52)", 1)
t = t.replace("const ARMORY_PREV := Rect2(60, 736, 60, 44)", "const ARMORY_PREV := Rect2(60, 722, 60, 44)", 1)
t = t.replace("const ARMORY_NEXT := Rect2(420, 736, 60, 44)", "const ARMORY_NEXT := Rect2(420, 722, 60, 44)", 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
print("armory layout tightened")
