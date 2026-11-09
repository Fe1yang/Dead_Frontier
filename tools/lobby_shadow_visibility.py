import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if is_instance_valid(bike): bike.visible=focus_vehicle
	if is_instance_valid(pet): pet.visible=focus_pets'''
new = '''	if is_instance_valid(bike): bike.visible=focus_vehicle
	if is_instance_valid(pet): pet.visible=focus_pets
	# shadows follow their owner: a lone blob under an empty rug looks like a bug
	if is_instance_valid(bike_shadow): bike_shadow.visible=focus_vehicle
	if is_instance_valid(pet_shadow): pet_shadow.visible=focus_pets'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("lobby shadows now follow their models")
