import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

added = 0
for i, line in enumerate(lines):
    s = line.strip()
    # dictionary style dispatch: "shop": _draw_shop()
    if s == '"shop": _draw_shop(),' or s == '"shop": _draw_shop()]' or s == '"shop": _draw_shop(),':
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = line.rstrip(",").rstrip("]") + ",\n" + indent + '"armory": _draw_armory()' + ("," if line.rstrip().endswith(",") else "]")
        added += 1
    # elif style
    elif s == 'elif game.state=="shop": _draw_shop()':
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = line + "\n" + indent + 'elif game.state=="armory": _draw_armory()'
        added += 1

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("routes added:", added)
