import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

out = []
skip_empty_elif = False
for i, line in enumerate(lines):
    if line.strip() == "elif game.lobby_tab==4:":
        # the weapon tab has no equip switch any more; drop the empty branch
        skip_empty_elif = True
        continue
    if skip_empty_elif:
        skip_empty_elif = False
        if line.strip() == "":
            continue
    out.append(line)

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("empty elif removed")
