import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '\t\t"jockey": rate=randf_range(1.18,1.30)'
new = ('\t\t\t"jockey":\n'
       '\t\t\t\t# the jockey sprints at 7.4 m/s on a dog run cycle; at ~1.2x it skated along the road\n'
       '\t\t\t\trate = clampf(1.35 + (speed - 3.5) * 0.22, 1.35, 2.6)')
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey stride rate follows its speed")
