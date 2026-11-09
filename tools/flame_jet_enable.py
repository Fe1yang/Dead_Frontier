import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''\tplayer.fire()
\t# The particle jet is parked until it can be tested on device: on screen it covered the
\t# camera in a red wash. Damage and sound are unaffected.
\tsound.play("flame")'''
new = '''\tplayer.fire()
\tplayer.pulse_flame()
\tsound.play("flame")'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame jet re-enabled")
