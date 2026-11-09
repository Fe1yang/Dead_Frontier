import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) street props: both passes were placing them 11 m out, inside the building shell
p = ROOT + r"\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()
old = "\tvar x: float = side * 11.0"
new = ("\t# 8.85 m is the pavement line; 11 m sits inside the building shell, so props placed there\n"
       "\t# were invisible.\n"
       "\tvar x: float = side * 8.85")
n = t.count(old)
t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("prop line patched in", n, "places")

# 2) lighter orange flame
p2 = ROOT + r"\scripts\player_3d.gd"
h = io.open(p2, encoding="utf-8").read()

pairs = (
    ('\tramp.set_color(0, Color(1.0, 0.86, 0.45, 0.0))', '\tramp.set_color(0, Color(1.0, 0.95, 0.70, 0.0))'),
    ('\tramp.add_point(0.06, Color(1.0, 0.82, 0.38, 0.85))', '\tramp.add_point(0.06, Color(1.0, 0.90, 0.55, 0.90))'),
    ('\tramp.add_point(0.22, Color(1.0, 0.70, 0.20, 0.82))', '\tramp.add_point(0.22, Color(1.0, 0.78, 0.35, 0.85))'),
    ('\tramp.add_point(0.45, Color(1.0, 0.62, 0.16, 0.70))', '\tramp.add_point(0.45, Color(1.0, 0.66, 0.22, 0.65))'),
    ('\tramp.add_point(0.72, Color(1.0, 0.46, 0.12, 0.40))', '\tramp.add_point(0.72, Color(0.95, 0.55, 0.16, 0.35))'),
    ('\tramp.set_color(3, Color(0.55, 0.24, 0.06, 0.0))', '\tramp.set_color(3, Color(0.80, 0.42, 0.10, 0.0))'),
)
changed = 0
for old, new in pairs:
    if h.count(old) == 1:
        h = h.replace(old, new, 1)
        changed += 1
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("flame ramp lightened:", changed, "stops")
