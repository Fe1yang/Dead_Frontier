import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

pairs = [
    (
        "func character_owned(index: int) -> bool:\n",
        "func character_owned(index: int) -> bool:\n\tif all_access: return true\n",
    ),
    (
        "func vehicle_is_owned(id: String) -> bool:\n",
        "func vehicle_is_owned(id: String) -> bool:\n\tif all_access: return true\n",
    ),
]

for old, new in pairs:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

# pets and skins use the same pattern
for fn in ("func pet_owned(index: int) -> bool:", "func skin_owned(index: int) -> bool:"):
    if fn in t and "if all_access: return true" not in t.split(fn)[1][:80]:
        t = t.replace(fn, fn + "\n\tif all_access: return true", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("all_access unlocks characters, pets, skins and vehicles")
