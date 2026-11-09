import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\tif is_instance_valid(torch):\n\t\ttorch.position=muzzle+aim_direction*0.08+Vector3(0,-0.04,0)"
new = """\tif is_instance_valid(torch):
\t\t# In a vehicle the lamp belongs at the front bumper, not at the rider's hand: the beam
\t\t# used to start from the middle of the car and looked wrong.
\t\tif vehicle != "":
\t\t\ttorch.position = Vector3(0.0, 0.78, -1.75)
\t\telse:
\t\t\ttorch.position=muzzle+aim_direction*0.08+Vector3(0,-0.04,0)"""
assert t.count(old) == 1
t = t.replace(old, new, 1)

old_spill = "\t\tif is_instance_valid(torch_spill): torch_spill.position=muzzle-aim_direction*0.30"
new_spill = """\t\tif is_instance_valid(torch_spill):
\t\t\ttorch_spill.position = Vector3(0.0, 0.62, -1.55) if vehicle != "" else muzzle-aim_direction*0.30"""
assert t.count(old_spill) == 1
t = t.replace(old_spill, new_spill, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("vehicle lamp moved to the front bumper")
