import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\nadd_child(pet); pet.set_meta(\"lobby_pet\", true); ModelFix.double_sided(pet)"
new = "\n\tadd_child(pet); pet.set_meta(\"lobby_pet\", true); ModelFix.double_sided(pet)"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("restored the add_child indentation")
