import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
h = io.open(p, encoding="utf-8").read()

pairs = (
    ('\tramp.set_color(0, Color(1.0, 0.86, 0.45, 0.0))', '\tramp.set_color(0, Color(1.0, 0.60, 0.16, 0.0))'),
    ('\tramp.add_point(0.06, Color(1.0, 0.82, 0.38, 0.85))', '\tramp.add_point(0.06, Color(1.0, 0.62, 0.16, 0.85))'),
    ('\tramp.add_point(0.22, Color(1.0, 0.70, 0.20, 0.82))', '\tramp.add_point(0.22, Color(1.0, 0.55, 0.12, 0.82))'),
    ('\tramp.add_point(0.45, Color(1.0, 0.62, 0.16, 0.70))', '\tramp.add_point(0.45, Color(0.90, 0.40, 0.08, 0.66))'),
    ('\tramp.add_point(0.72, Color(1.0, 0.46, 0.12, 0.40))', '\tramp.add_point(0.72, Color(0.72, 0.26, 0.05, 0.34))'),
    ('\tramp.set_color(3, Color(0.55, 0.24, 0.06, 0.0))', '\tramp.set_color(3, Color(0.45, 0.18, 0.05, 0.0))'),
)
for old, new in pairs:
    assert h.count(old) == 1, old
    h = h.replace(old, new, 1)

if "the particle texture has a white core" not in h:
    old_line = "\tmat.albedo_texture = load(\"res://assets/vfx/flame_particle.png\")"
    new_line = (old_line + "\n\t# the particle texture has a white core; tint it orange so the tips never read white\n"
                "\tmat.albedo_color = Color(1.0, 0.55, 0.15, 1.0)")
    assert h.count(old_line) == 1
    h = h.replace(old_line, new_line, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("flame ramp and tint are fully orange")
