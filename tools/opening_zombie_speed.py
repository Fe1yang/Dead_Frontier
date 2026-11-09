import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\t\t_spawn_zombie(-18); _spawn_zombie(-32); _spawn_companion()"
new = '''\t\t_spawn_zombie(-18); _spawn_zombie(-32); _spawn_companion()
\t\t# These two open the run, and a walker's own speed is roughly the road speed, so it used to
\t\t# hover in place instead of closing in. Give the opening pair a real approach speed.
\t\tfor opening_z in zombies:
\t\t\tif is_instance_valid(opening_z) and opening_z.kind != "banshee":
\t\t\t\topening_z.speed = 3.5 + 2.2'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("opening zombies now actually close in")
