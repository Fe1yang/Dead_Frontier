import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) no white at the nozzle: start warm yellow instead of near-white
repl = (
    ("\tramp.set_color(0, Color(1.0, 0.95, 0.80, 0.0))", "\tramp.set_color(0, Color(1.0, 0.86, 0.45, 0.0))"),
    ("\tramp.add_point(0.06, Color(1.0, 0.90, 0.60, 0.85))", "\tramp.add_point(0.06, Color(1.0, 0.82, 0.38, 0.85))"),
    ("\tramp.add_point(0.22, Color(1.0, 0.72, 0.22, 0.80))", "\tramp.add_point(0.22, Color(1.0, 0.70, 0.20, 0.82))"),
)
for old, new in repl:
    if t.count(old) == 1:
        t = t.replace(old, new, 1)

# 2) a longer trail: particles live longer and leave faster, so the jet reads as a stream
repl2 = (
    ("\tjet.lifetime = 0.34", "\tjet.lifetime = 0.62"),
    ("\tjet.initial_velocity_min = 7.0", "\tjet.initial_velocity_min = 11.0"),
    ("\tjet.initial_velocity_max = 10.5", "\tjet.initial_velocity_max = 17.0"),
    ("\tjet.amount = 320", "\tjet.amount = 260"),
)
for old, new in repl2:
    if t.count(old) == 1:
        t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame starts warm yellow and reaches further")
