import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

old = "_bold_text(id, Vector2(60, 610), 24, WHITE)"
assert h.count(old) == 1, h.count(old)
h = h.replace(old, "_bold_text(id, Vector2(60, 552), 24, WHITE)", 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("weapon name moved above the bars")
