import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) the settings gear reads as an outline button: white border, white gear
p = ROOT + r"\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()
old = '''func _lobby_settings_gear(r: Rect2) -> void:
	_panel(r, Color(0.06,0.07,0.075,0.92), Color(0.55,0.57,0.58,0.9), 1)
	_gear_icon(r.get_center(), 0.62, Color(0.86,0.87,0.88))'''
new = '''func _lobby_settings_gear(r: Rect2) -> void:
	_panel(r, Color(0.06,0.07,0.075,0.92), WHITE, 1)
	_gear_icon(r.get_center(), 0.62, WHITE)'''
assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("settings gear is white")

# 2) right column lines up with the gear's right edge (534)
p2 = ROOT + r"\scripts\main_3d.gd"
t = io.open(p2, encoding="utf-8").read()
replaced = 0
for y in (118, 198, 358, 438, 518, 598):
    old_r = "Rect2(462,%d,70,76)" % y
    if old_r in t:
        t = t.replace(old_r, "Rect2(464,%d,70,76)" % y)
        replaced += 1
io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
print("side icons shifted to the gear edge:", replaced)
