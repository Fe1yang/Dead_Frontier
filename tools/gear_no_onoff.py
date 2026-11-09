import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(p, encoding="utf-8").read()

start = h.find("func _gear_button(r: Rect2,on: bool) -> void:")
assert start > 0
end = h.find("func _gear_icon(", start)
assert end > start

new = '''func _gear_button(r: Rect2,on: bool) -> void:
	# No ON/OFF text: an equipped item shows a gold ring, an unequipped one a white ring.
	var tint: Color = Color(1.0, 0.86, 0.4) if on else WHITE
	_panel(r, Color(0.06,0.065,0.07,0.9), tint, 1)
	_gear_icon(r.get_center(), 0.62, tint)


'''
h = h[:start] + new + h[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("ON/OFF labels removed from the gear buttons")
