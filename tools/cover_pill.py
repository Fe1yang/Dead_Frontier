import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old_start = t.find("\t# The poster art carries no prompt, so the cover draws its own")
old_end = t.find("func _draw_loading()")
assert old_start > 0 and old_end > old_start

new = '''	# The prompt is part of the cover: a bordered pill sitting on the poster, pulsing so it reads
	# as the thing to tap rather than as a caption.
	var pulse: float=0.55+0.45*sin(float(Time.get_ticks_msec())*0.0032)
	var hint: String="点击任意处开始" if String(game.language_code).begins_with("zh") else "TOUCH ANYWHERE TO START"
	var hy: float=game.ui_h-86.0
	var hw: float=bold.get_string_size(hint,HORIZONTAL_ALIGNMENT_LEFT,-1,18).x
	var pill:=Rect2(270.0-hw*0.5-26.0,hy-30.0,hw+52.0,46.0)
	draw_rect(pill,Color(0.02,0.03,0.05,0.62))
	draw_rect(pill,Color(0.95,0.72,0.32,pulse),false,2.0)
	draw_string(bold,Vector2(pill.position.x+(pill.size.x-hw)*0.5,hy),hint,HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color(1.0,0.95,0.78,pulse))


'''
t = t[:old_start] + new + t[old_end:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("cover prompt is now a bordered pill")
