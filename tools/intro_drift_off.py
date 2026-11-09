import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\t\tz.position=Vector3(offset.x+sin(intro_time*3.0+i)*0.07,0,player.position.z+offset.z-intro_time*0.16)"
new = "\t\t# no backward drift: the horde keeps pace with the survivor instead of sliding behind him\n\t\tz.position=Vector3(offset.x+sin(intro_time*3.0+i)*0.07,0,player.position.z+offset.z)"

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("intro horde no longer drifts backwards")
