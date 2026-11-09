import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\zombie_3d.gd"
t = io.open(p, encoding="utf-8").read()

old_lean = "const JOCKEY_LEAN_DEG:=58.0"
new_lean = "const JOCKEY_LEAN_DEG:=42.0"
assert t.count(old_lean) == 1
t = t.replace(old_lean, new_lean, 1)

old_drop = "const JOCKEY_DROP:=-0.30"
new_drop = "const JOCKEY_DROP:=0.02"
assert t.count(old_drop) == 1
t = t.replace(old_drop, new_drop, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("jockey: lean 42 deg, lifted off the road")
