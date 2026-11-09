import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "return Rect2(c.position.x-6.0,c.position.y-58.0,c.size.x+12.0,50.0)"
new = "return Rect2(c.position.x-6.0,c.position.y-96.0,c.size.x+12.0,50.0)"
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("dropdown floats above the tab row")
