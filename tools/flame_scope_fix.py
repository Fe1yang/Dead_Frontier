import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# flat_fwd is declared inside the zombie loop; hoist it above both loops
old = "\tvar hit := 0\n"
new = "\tvar hit := 0\n\tvar flat_fwd: Vector3 = Vector3(fwd.x, 0.0, fwd.z).normalized()\n"
assert t.count(old) == 1
t = t.replace(old, new, 1)

# the inner declaration is now redundant
old2 = "\t\tvar flat_fwd: Vector3 = Vector3(fwd.x, 0.0, fwd.z).normalized()\n"
assert t.count(old2) == 1, t.count(old2)
t = t.replace(old2, "", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flat_fwd hoisted so the crate/barrel cone can use it")
