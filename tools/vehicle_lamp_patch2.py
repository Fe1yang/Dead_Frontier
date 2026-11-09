import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old_torch = "\t\ttorch.position=muzzle+aim_direction*0.08+Vector3(0,-0.04,0)"
new_torch = (
    "\t\t# In a vehicle the lamp belongs at the front bumper, not at the rider's hand: the beam\n"
    "\t\t# used to start from the middle of the car and looked wrong.\n"
    "\t\tif vehicle != \"\":\n"
    "\t\t\ttorch.position = Vector3(0.0, 0.78, -1.75)\n"
    "\t\telse:\n"
    "\t\t\ttorch.position=muzzle+aim_direction*0.08+Vector3(0,-0.04,0)"
)
assert t.count(old_torch) == 1
t = t.replace(old_torch, new_torch, 1)

old_spill = "\tif is_instance_valid(torch_spill): torch_spill.position=muzzle-aim_direction*0.30"
new_spill = (
    "\tif is_instance_valid(torch_spill):\n"
    "\t\ttorch_spill.position = Vector3(0.0, 0.62, -1.55) if vehicle != \"\" else muzzle-aim_direction*0.30"
)
assert t.count(old_spill) == 1
t = t.replace(old_spill, new_spill, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("vehicle lamp moved to the front bumper")
