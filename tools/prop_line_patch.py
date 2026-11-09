import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\tvar x: float = side * 11.0"
new = ("\t# The pavement line is 8.8 m from the centre; 11 m sits inside the building shell, which is\n"
       "\t# why benches and bins placed here never showed up.\n"
       "\tvar x: float = side * 8.85")
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("street prop line moved from x=11 to the pavement at 8.85")
