import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\project.godot"
t = io.open(p, encoding="utf-8").read()

old = 'window/stretch/mode="canvas_items"'
new = 'window/stretch/mode="canvas_items"\nwindow/stretch/aspect="expand"'

assert t.count(old) == 1, t.count(old)
if 'window/stretch/aspect' not in t:
    t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("stretch aspect -> expand (fills the iPhone screen instead of letterboxing)")
