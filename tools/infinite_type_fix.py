import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

t = t.replace("var infw:=game.infinite_resources()", "var infw: bool = game.infinite_resources()")
t = t.replace("var infw2:=game.infinite_resources()", "var infw2: bool = game.infinite_resources()")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("typed the wallet flags")
