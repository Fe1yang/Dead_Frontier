import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	var coin_x: float=470.0
	var coin_y: float=118.0
	draw_string(bold,Vector2(coin_x,coin_y),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("f2c14e"))
	if game.run_silver > 0:
		draw_string(bold,Vector2(coin_x,coin_y+24),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("cfd6dd"))'''

new = '''	# right aligned against the screen edge so long numbers never clip
	var coin_right: float=526.0
	var gw: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20).x
	draw_string(bold,Vector2(coin_right-gw,138.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("f2c14e"))
	if game.run_silver > 0:
		var sw: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20).x
		draw_string(bold,Vector2(coin_right-sw,162.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("cfd6dd"))'''

assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("coin text right aligned lower")
