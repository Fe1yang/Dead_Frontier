import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	# kills and coins picked up this run, side by side under the distance
	var kill_txt:="x %d"%game.kills; var coin_txt:=_group_thousands(game.run_coins)
	var kw: float=bold.get_string_size(kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36).x
	var cw: float=bold.get_string_size(coin_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36).x
	var row_w: float=24.0+kw+28.0+34.0+cw
	var rx: float=270.0-row_w*0.5
	_draw_skull(Vector2(rx+12,118),17)
	draw_string(bold,Vector2(rx+24,133),kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36,WHITE)
	var cx: float=rx+24.0+kw+28.0
	_draw_coin_stack(Vector2(cx+14,118),13)
	draw_string(bold,Vector2(cx+34,133),coin_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36,WHITE)'''

new = '''	# Kills only, centred under the distance. The coins moved to the top-right column so the
	# middle of the screen stays clean: gold and silver as coloured text, no extra icons.
	var kill_txt:="x %d"%game.kills
	var kw: float=bold.get_string_size(kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36).x
	var rx: float=270.0-(24.0+kw)*0.5
	_draw_skull(Vector2(rx+12,118),17)
	draw_string(bold,Vector2(rx+24,133),kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36,WHITE)
	var gold_txt:="金币 x %d" % game.run_coins if String(game.language_code).begins_with("zh") else "GOLD x %d" % game.run_coins
	var silver_txt:="银币 x %d" % game.run_silver if String(game.language_code).begins_with("zh") else "SILVER x %d" % game.run_silver
	var coin_x: float=470.0
	var coin_y: float=118.0
	draw_string(bold,Vector2(coin_x,coin_y),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("f2c14e"))
	if game.run_silver > 0:
		draw_string(bold,Vector2(coin_x,coin_y+24),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("cfd6dd"))'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("HUD: skull centred, gold/silver text top-right")
