import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

repl = (
    ("\tjet.amount = 240", "\tjet.amount = 150"),
    ("\tjet.lifetime = 0.85", "\tjet.lifetime = 0.55"),
    ("\tjet.initial_velocity_min = 14.0", "\tjet.initial_velocity_min = 11.0"),
    ("\tjet.initial_velocity_max = 22.0", "\tjet.initial_velocity_max = 16.0"),
    ("\tjet.scale_amount_min = 0.85", "\tjet.scale_amount_min = 0.45"),
    ("\tjet.scale_amount_max = 2.3", "\tjet.scale_amount_max = 1.15"),
    ("\tgrow.add_point(Vector2(0.0, 0.35))", "\tgrow.add_point(Vector2(0.0, 0.30))"),
    ("\tgrow.add_point(Vector2(0.35, 1.0))", "\tgrow.add_point(Vector2(0.35, 0.85))"),
    ("\tgrow.add_point(Vector2(1.0, 1.35))", "\tgrow.add_point(Vector2(1.0, 0.75))"),
    ("\tquad.size = Vector2(0.85, 0.85)", "\tquad.size = Vector2(0.40, 0.40)"),
    ("\tglow.omni_range = 7.5", "\tglow.omni_range = 5.0"),
    ("\t\tflame_glow.light_energy = 3.4", "\t\tflame_glow.light_energy = 1.5"),
)

for old, new in repl:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame jet toned down to a readable cone")
