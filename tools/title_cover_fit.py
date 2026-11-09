import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = "\tif menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,game.ui_h),false)"
new = '''	if menu_art:
		# cover fit: the poster always fills the height, and any extra width is cropped away
		var tw := float(menu_art.get_width())
		var th := float(menu_art.get_height())
		var k := maxf(game.ui_h / th, 540.0 / tw)
		var sz := Vector2(tw * k, th * k)
		draw_texture_rect(menu_art, Rect2(Vector2((540.0 - sz.x) * 0.5, (game.ui_h - sz.y) * 0.5), sz), false)'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("title poster is cover-fitted")
