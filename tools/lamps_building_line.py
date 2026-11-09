import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

pairs = (
    ("Vector3(side * 5.20, PAVEMENT_Y, base_z + 2.4)", "Vector3(side * 7.05, PAVEMENT_Y, base_z + 2.4)"),
    ("Vector3(side * 5.20, PAVEMENT_Y, base_z - 5.4)", "Vector3(side * 7.05, PAVEMENT_Y, base_z - 5.4)"),
)
for old, new in pairs:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("lamps moved to the building line (x = 7.05)")
