import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	# A green sphere-like prop (the ceramic pots) pokes through the door slab; drop the pots.
	for pot_name in ["Safe_ceramic", "Safe_ceramic_blue"]:'''
new = '''	# A green sphere pokes through the door slab. The ceramic pots were not it, so take out every
	# small round decoration that could be sitting behind the blast door.
	for pot_name in ["Safe_ceramic", "Safe_ceramic_blue", "Safe_lamp_glow", "Safe_ember",
			"Safe_led_green", "Safe_led_amber", "Safe_olive_light"]:'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("door-area round props hidden")
