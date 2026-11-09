import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '\t_text("LV %d / %d"%[level,item.max_level],Vector2(232,747),13,GOLD)'
new = ('\t# level text sits just past the last pip and matches the pip height\n'
       '\tvar lv_x: float=53.0+float(item.max_level)*40.0+14.0\n'
       '\t_text("LV %d / %d"%[level,item.max_level],Vector2(lv_x,747),16,GOLD)')

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("level text moved right of the pips and enlarged")
