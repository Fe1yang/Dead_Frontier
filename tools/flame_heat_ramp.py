import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# t=0 is the frame the particle is born at the nozzle, so the hottest white belongs there and the
# colour cools white -> yellow -> orange as the flame travels.
wanted = [
    "\tramp.set_color(0, Color(1.0, 1.0, 1.0, 0.0))",
    "\tramp.add_point(0.05, Color(1.0, 1.0, 0.92, 0.95))",
    "\tramp.add_point(0.20, Color(1.0, 0.93, 0.50, 0.90))",
    "\tramp.add_point(0.45, Color(1.0, 0.72, 0.22, 0.80))",
    "\tramp.add_point(0.72, Color(1.0, 0.50, 0.10, 0.45))",
    "\tramp.set_color(3, Color(0.85, 0.34, 0.06, 0.0))",
]

idx = 0
for i, line in enumerate(lines):
    if line.startswith("\tramp.set_color(0,") or line.startswith("\tramp.add_point(0.05,") \
       or line.startswith("\tramp.add_point(0.06,") or line.startswith("\tramp.add_point(0.20,") \
       or line.startswith("\tramp.add_point(0.22,") or line.startswith("\tramp.add_point(0.45,") \
       or line.startswith("\tramp.add_point(0.72,") or line.startswith("\tramp.set_color(3,"):
        if idx < len(wanted):
            lines[i] = wanted[idx]
            idx += 1

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("ramp stops written:", idx)
