import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "var pet_base_yaw" not in t:
    t = t.replace(
        'var pet_path:=""',
        'var pet_path:=""\n## Resting facing of the current pet model: some assets are authored side-on.\nvar pet_base_yaw:=0.0',
        1,
    )

old_set = "\tpet.rotation.y=yaw"
if "pet_base_yaw=yaw" not in t:
    assert t.count(old_set) == 1
    t = t.replace(old_set, "\tpet_base_yaw=yaw\n\tpet.rotation.y=yaw", 1)

old_spin = "\t\tif spin_pet: pet.rotation.y=spin"
new_spin = "\t\tif spin_pet: pet.rotation.y=pet_base_yaw+spin"
assert t.count(old_spin) == 1
t = t.replace(old_spin, new_spin, 1)

old_idle = "\t\telse: pet.rotation.y=lerp_angle(pet.rotation.y,0.0,1.0-exp(-delta*1.2))"
new_idle = "\t\telse: pet.rotation.y=lerp_angle(pet.rotation.y,pet_base_yaw,1.0-exp(-delta*1.2))"
assert t.count(old_idle) == 1
t = t.replace(old_idle, new_idle, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pet base yaw is applied to spin and idle")
