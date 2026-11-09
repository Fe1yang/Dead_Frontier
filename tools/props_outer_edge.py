import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The pavement runs out to about 7.8 m, so use the outer half of it.
repl = (
    ("var x_wall: float = side * 7.10", "var x_wall: float = side * 7.55"),
    ("side * 6.60", "side * 7.35"),
    ("side * 6.35", "side * 7.05"),
    ("side * 6.15", "side * 6.95"),
    ("side * 6.20 + decor_rng.randf_range(-0.15, 0.15)", "side * 7.10 + decor_rng.randf_range(-0.15, 0.15)"),
    ("decor_rng.randf_range(6.0, 7.4)", "decor_rng.randf_range(6.9, 7.75)"),
)
for old, new in repl:
    assert t.count(old) >= 1, old
    t = t.replace(old, new)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props moved to the outer pavement, 6.95..7.55 m")
