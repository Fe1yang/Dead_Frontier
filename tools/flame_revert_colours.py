import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

original = [
    "\tramp.set_color(0, Color(1.0, 0.86, 0.45, 0.0))",
    "\tramp.add_point(0.06, Color(1.0, 0.82, 0.38, 0.85))",
    "\tramp.add_point(0.22, Color(1.0, 0.70, 0.20, 0.82))",
    "\tramp.add_point(0.45, Color(1.0, 0.62, 0.16, 0.70))",
    "\tramp.add_point(0.72, Color(1.0, 0.46, 0.12, 0.40))",
    "\tramp.set_color(3, Color(0.55, 0.24, 0.06, 0.0))",
]

idx = 0
drop = []
for i, line in enumerate(lines):
    if line.startswith("\tramp.set_color(0,") or line.startswith("\tramp.add_point(0.06,") \
       or line.startswith("\tramp.add_point(0.22,") or line.startswith("\tramp.add_point(0.45,") \
       or line.startswith("\tramp.add_point(0.72,") or line.startswith("\tramp.set_color(3,"):
        lines[i] = original[idx]
        idx += 1
    elif "the particle texture has a white core" in line or line.strip() == "mat.albedo_color = Color(1.0, 0.55, 0.15, 1.0)":
        drop.append(i)

for i in reversed(drop):
    del lines[i]

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("ramp restored:", idx, "tint lines removed:", len(drop))
