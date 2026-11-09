import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) the spray is too loud
sp = base + r"\sound.gd"
s = io.open(sp, encoding="utf-8").read()
old = '\telif id=="flame": voice.volume_db=-13.0'
new = '\telif id=="flame": voice.volume_db=-19.0'
assert s.count(old) == 1
s = s.replace(old, new, 1)
io.open(sp, "w", encoding="utf-8", newline="\n").write(s)
print("flame volume -13 -> -19 dB")

# 2) keep the flame yellow and orange, drop the red the jet cooled into
pp = base + r"\player_3d.gd"
p = io.open(pp, encoding="utf-8").read()
repl = (
    ("\tramp.add_point(0.45, Color(0.95, 0.42, 0.08, 0.65))", "\tramp.add_point(0.45, Color(1.0, 0.62, 0.16, 0.70))"),
    ("\tramp.add_point(0.72, Color(0.78, 0.18, 0.04, 0.45))", "\tramp.add_point(0.72, Color(1.0, 0.46, 0.12, 0.40))"),
    ("\tramp.set_color(3, Color(0.12, 0.09, 0.08, 0.0))", "\tramp.set_color(3, Color(0.55, 0.24, 0.06, 0.0))"),
)
for old_c, new_c in repl:
    if p.count(old_c) == 1:
        p = p.replace(old_c, new_c, 1)
io.open(pp, "w", encoding="utf-8", newline="\n").write(p)
print("flame ramp: yellow/orange only")
