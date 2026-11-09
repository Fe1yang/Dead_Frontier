import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\lobby_scene_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	for pot_name in ["Safe_ceramic", "Safe_ceramic_blue", "Safe_lamp_glow", "Safe_ember",
			"Safe_led_green", "Safe_led_amber", "Safe_olive_light"]:'''
new = '''	for pot_name in ["Safe_ceramic", "Safe_ceramic_blue", "Safe_lamp_glow", "Safe_ember"]:'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("kept the hide list to small decor only")
