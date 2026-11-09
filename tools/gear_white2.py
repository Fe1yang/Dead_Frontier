import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

old = '''func _gear_button(r: Rect2,on: bool) -> void:
	var tint: Color = Color(1.0,0.86,0.4) if on else Color(0.45,0.46,0.47)
	_panel(r,Color(0.06,0.065,0.07,0.9) if on else Color(0.03,0.032,0.035,0.75),tint,1)
	_gear_icon(r.get_center()+Vector2(0,-5),0.55,tint)
	var label: String = "ON" if on else "OFF"
	_text_center(label,Vector2(r.get_center().x,r.end.y-8),11,tint)'''

new = '''func _gear_button(r: Rect2,on: bool) -> void:
	# the ring and the gear stay white like the settings button; only the ON/OFF label carries
	# the equipped state
	_panel(r,Color(0.06,0.065,0.07,0.9) if on else Color(0.05,0.052,0.055,0.85),WHITE,1)
	_gear_icon(r.get_center()+Vector2(0,-5),0.55,WHITE)
	var label: String = "ON" if on else "OFF"
	_text_center(label,Vector2(r.get_center().x,r.end.y-8),11,Color(1.0,0.86,0.4) if on else Color(0.62,0.63,0.64))'''

assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("gear toggles are white")
