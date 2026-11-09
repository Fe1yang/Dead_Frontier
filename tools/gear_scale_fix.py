import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	_gear_icon(r.get_center(), r.size.y * 0.26, Color(0.86,0.87,0.88))'''
new = '''	_gear_icon(r.get_center(), 0.62, Color(0.86,0.87,0.88))'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("gear icon scaled to fit the button")
