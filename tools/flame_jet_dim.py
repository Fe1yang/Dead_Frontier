import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

repl = (
    # the muzzle light was lighting the whole street: keep a hint of glow, not a floodlight
    ("\tglow.omni_range = 5.0", "\tglow.omni_range = 3.2"),
    ("\t\tflame_glow.light_energy = 1.5", "\t\tflame_glow.light_energy = 0.35"),
    # additive blending was what turned the cone into a white sheet
    ("\tmat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD\n", "\tmat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX\n"),
    # softer, more saturated ramp
    ("\tramp.add_point(0.22, Color(1.0, 0.86, 0.35, 0.98))", "\tramp.add_point(0.22, Color(1.0, 0.72, 0.22, 0.80))"),
    ("\tramp.add_point(0.45, Color(1.0, 0.52, 0.10, 0.90))", "\tramp.add_point(0.45, Color(0.95, 0.42, 0.08, 0.65))"),
    ("\tramp.set_color(0, Color(1.0, 1.0, 0.92, 0.0))", "\tramp.set_color(0, Color(1.0, 0.95, 0.80, 0.0))"),
    ("\tramp.add_point(0.06, Color(1.0, 1.0, 0.85, 1.0))", "\tramp.add_point(0.06, Color(1.0, 0.90, 0.60, 0.85))"),
)

for old, new in repl:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame dimmed: mix blend, weak light, softer ramp")
