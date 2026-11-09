import io

# 1) crate preview scales
p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\weapon_crate_3d.gd"
t = io.open(p, encoding="utf-8").read()
old = '"HELMET":1.8'
assert t.count(old) == 1, old
t = t.replace(old, '"HELMET":0.95', 1)
old_fuel = '"FUEL":1.15'
assert t.count(old_fuel) == 1
t = t.replace(old_fuel, '"FUEL":0.82', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("crate scales: helmet 1.8 -> 0.95, fuel 1.15 -> 0.82")

# 2) flame jet: no white core, all orange
p2 = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
h = io.open(p2, encoding="utf-8").read()

pairs = (
    ('\tramp.set_color(0, Color(1.0, 0.95, 0.80, 0.0))', '\tramp.set_color(0, Color(1.0, 0.62, 0.20, 0.0))'),
    ('\tramp.add_point(0.06, Color(1.0, 0.90, 0.60, 0.85))', '\tramp.add_point(0.06, Color(1.0, 0.66, 0.20, 0.85))'),
    ('\tramp.add_point(0.22, Color(1.0, 0.72, 0.22, 0.80))', '\tramp.add_point(0.22, Color(1.0, 0.55, 0.12, 0.80))'),
    ('\tramp.add_point(0.45, Color(0.95, 0.42, 0.08, 0.65))', '\tramp.add_point(0.45, Color(0.85, 0.32, 0.05, 0.60))'),
    ('\tmat.vertex_color_use_as_albedo = true', '\tmat.vertex_color_use_as_albedo = true\n\t# the particle texture has a white core; tint it orange so the flame tips are never white\n\tmat.albedo_color = Color(1.0, 0.58, 0.18, 1.0)'),
)
for old, new in pairs:
    assert h.count(old) == 1, old
    h = h.replace(old, new, 1)

io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("flame tinted orange, white core removed")
