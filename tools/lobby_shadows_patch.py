import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

# pet shadow: the variable existed but was never created, so pets stood with no contact shadow
old_pet = "\tpet.position=STAND+Vector3(0,ModelFix.fit_pet(pet,length*ACTOR_SCALE),0)"
new_pet = (
    "\tpet.position=STAND+Vector3(0,ModelFix.fit_pet(pet,length*ACTOR_SCALE),0)\n"
    "\tvar pet_span := length * ACTOR_SCALE\n"
    "\tpet_shadow = _blob_shadow(Vector2(pet_span * 0.92, pet_span * 0.62), STAND + Vector3(0, 0.021, 0.02))"
)
assert t.count(old_pet) == 1
t = t.replace(old_pet, new_pet, 1)

# vehicle shadow: same blob under the bike, sized from its own footprint
old_bike = "\t_fit_vehicle()\n"
new_bike = (
    "\t_fit_vehicle()\n"
    "\tif is_instance_valid(bike_shadow):\n"
    "\t\tbike_shadow.queue_free()\n"
    "\tbike_shadow = _blob_shadow(Vector2(2.5, 1.15), STAND + Vector3(0, 0.021, -0.30))\n"
)
assert t.count(old_bike) == 1
t = t.replace(old_bike, new_bike, 1)

if "var bike_shadow" not in t:
    t = t.replace("var pet_shadow: MeshInstance3D", "var pet_shadow: MeshInstance3D\nvar bike_shadow: MeshInstance3D", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pet and vehicle contact shadows added")
