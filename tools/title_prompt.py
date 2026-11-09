import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,game.ui_h),false)
	else: draw_rect(Rect2(0,0,540,game.ui_h),INK)'''
new = '''	if menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,game.ui_h),false)
	else: draw_rect(Rect2(0,0,540,game.ui_h),INK)
	# The Dreadline poster has no prompt painted on it, so draw it here.
	var lang_t: String = game.language_code
	var prompt: String = "点任意处开始" if String(lang_t).begins_with("zh") else "TAP ANYWHERE TO START"
	var pulse: float = 0.55 + 0.45 * sin(Time.get_ticks_msec() * 0.003)
	_clean_center(bold, Vector2(270.0, game.ui_h - 150.0), prompt, 22, Color(1, 1, 1, pulse))
	_clean_center(bold, Vector2(270.0, game.ui_h - 96.0), "v1.0.0", 12, Color(1, 1, 1, 0.45))'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("tap prompt drawn on the Dreadline poster")
