import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

orange = [
    "\tramp.set_color(0, Color(1.0, 0.60, 0.16, 0.0))",
    "\tramp.add_point(0.06, Color(1.0, 0.62, 0.16, 0.85))",
    "\tramp.add_point(0.22, Color(1.0, 0.55, 0.12, 0.82))",
    "\tramp.add_point(0.45, Color(0.90, 0.40, 0.08, 0.66))",
    "\tramp.add_point(0.72, Color(0.72, 0.26, 0.05, 0.34))",
    "\tramp.set_color(3, Color(0.45, 0.18, 0.05, 0.0))",
]

replaced = 0
for i, line in enumerate(lines):
    if line.startswith("\tramp.set_color(0,") or line.startswith("\tramp.add_point(0.06,") \
       or line.startswith("\tramp.add_point(0.22,") or line.startswith("\tramp.add_point(0.45,") \
       or line.startswith("\tramp.add_point(0.72,") or line.startswith("\tramp.set_color(3,"):
        lines[i] = orange[replaced]
        replaced += 1

# tint the jet material so the texture's white core cannot show as white dots
for i, line in enumerate(lines):
    if line.strip() == 'mat.albedo_texture = load("res://assets/vfx/flame_particle.png")' and i > 600:
        lines.insert(i + 1, "\t# the particle texture has a white core; tint it so the tips stay orange")
        lines.insert(i + 2, "\tmat.albedo_color = Color(1.0, 0.55, 0.15, 1.0)")
        break

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("ramp lines replaced:", replaced)
