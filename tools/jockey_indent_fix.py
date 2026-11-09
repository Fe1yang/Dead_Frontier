import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

fixed = 0
for i, line in enumerate(lines):
    if line == '\t\t\t\t"jockey":':
        lines[i] = '\t\t\t"jockey":'
        fixed += 1
    elif line.strip().startswith('# the jockey sprints at 7.4 m/s'):
        lines[i] = '\t\t\t\t# the jockey sprints at 7.4 m/s on a dog run cycle; at ~1.2x it skated along'
        fixed += 1
    elif line.strip().startswith('rate = clampf(1.35 + (speed - 3.5) * 0.22'):
        lines[i] = '\t\t\t\trate = clampf(1.35 + (speed - 3.5) * 0.22, 1.35, 2.6)'
        fixed += 1

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("indentation fixed:", fixed)
