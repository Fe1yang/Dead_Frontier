import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	if menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,game.ui_h),false)
	else: draw_rect(Rect2(0,0,540,game.ui_h),INK)'''

new = '''	if menu_art: draw_texture_rect(menu_art,Rect2(0,0,540,game.ui_h),false)
	else: draw_rect(Rect2(0,0,540,game.ui_h),INK)
	# The poster art carries no prompt, so the cover draws its own: pulsing, bottom centre.
	var pulse: float=0.55+0.45*sin(float(Time.get_ticks_msec())*0.0032)
	var hint: String="点击任意处开始" if String(game.language_code).begins_with("zh") else "TOUCH ANYWHERE TO START"
	var hy: float=game.ui_h-64.0
	var hw: float=bold.get_string_size(hint,HORIZONTAL_ALIGNMENT_LEFT,-1,19).x
	draw_rect(Rect2(270.0-hw*0.5-16.0,hy-24.0,hw+32.0,38.0),Color(0,0,0,0.45))
	draw_string(bold,Vector2(270.0-hw*0.5,hy),hint,HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color(1.0,0.94,0.72,pulse))'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("cover prompt added")
