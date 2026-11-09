import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# Every prop moves a good half metre further out: at 4.6 they still hugged the kerb and read as
# road-side clutter. The pavement runs from the kerb at 4.36 out to the buildings near 7.8.
repl = (
    ("side * 4.62", "side * 5.15"),
    ("var x_wall: float = side * 6.55", "var x_wall: float = side * 6.95"),
    ("side * 5.45", "side * 6.05"),
    ("side * 5.25", "side * 5.90"),
    ("side * 4.90", "side * 5.45"),
    ("side * 5.35 + decor_rng.randf_range(-0.15, 0.15)", "side * 5.75 + decor_rng.randf_range(-0.15, 0.15)"),
    ("decor_rng.randf_range(4.55, 6.6)", "decor_rng.randf_range(5.1, 7.2)"),
)

for old, new in repl:
    assert t.count(old) >= 1, old
    t = t.replace(old, new)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("props pushed out to the middle of the pavement")
