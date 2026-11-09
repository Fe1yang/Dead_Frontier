import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

repl = (
    ("\tjet.amount = 150", "\tjet.amount = 320"),
    ("\tjet.lifetime = 0.55", "\tjet.lifetime = 0.34"),
    ("\tjet.spread = 9.0", "\tjet.spread = 5.0"),
    ("\tjet.gravity = Vector3(0, 2.2, 0)", "\tjet.gravity = Vector3(0, 1.0, 0)"),
    ("\tjet.initial_velocity_min = 11.0", "\tjet.initial_velocity_min = 7.0"),
    ("\tjet.initial_velocity_max = 16.0", "\tjet.initial_velocity_max = 10.5"),
    ("\tjet.scale_amount_min = 0.45", "\tjet.scale_amount_min = 0.55"),
    ("\tjet.scale_amount_max = 1.15", "\tjet.scale_amount_max = 1.25"),
    ("\tgrow.add_point(Vector2(0.0, 0.30))", "\tgrow.add_point(Vector2(0.0, 0.55))"),
    ("\tgrow.add_point(Vector2(0.35, 0.85))", "\tgrow.add_point(Vector2(0.35, 1.0))"),
    ("\tgrow.add_point(Vector2(1.0, 0.75))", "\tgrow.add_point(Vector2(1.0, 0.85))"),
    ("\tquad.size = Vector2(0.40, 0.40)", "\tquad.size = Vector2(0.26, 0.26)"),
)

for old, new in repl:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("engine-style dense short jet")
