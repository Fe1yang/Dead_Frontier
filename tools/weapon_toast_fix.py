import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '\tlobby_toast = 1.4\n\tlobby_toast_key = "weapon_on" if weapon_equipped else "weapon_off"\n'
new = '\t# the ON/OFF ring on the button is the feedback, no toast key needed\n'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("raw toast key removed")
