import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# 1) skull and the kill count must not overlap: the skull is r=17 wide, so start the text at +38
t = t.replace(
    "\tvar rx: float=270.0-(24.0+kw)*0.5\n\t_draw_skull(Vector2(rx+12,118),17)\n\tdraw_string(bold,Vector2(rx+24,133),kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,36,WHITE)",
    "\tvar rx: float=270.0-(38.0+kw)*0.5\n\t_draw_skull(Vector2(rx+14,118),16)\n\tdraw_string(bold,Vector2(rx+38,133),kill_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,34,WHITE)",
    1,
)

# 2) smaller coin text, silver always shown
old = '''	# right aligned against the screen edge so long numbers never clip
	var coin_right: float=526.0
	var gw: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20).x
	draw_string(bold,Vector2(coin_right-gw,138.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("f2c14e"))
	if game.run_silver > 0:
		var sw: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20).x
		draw_string(bold,Vector2(coin_right-sw,162.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("cfd6dd"))'''
new = '''	# right aligned, small, both currencies always visible so the player can read the stock
	var coin_right: float=524.0
	var gw: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	draw_string(bold,Vector2(coin_right-gw,140.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("f2c14e"))
	var sw: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	draw_string(bold,Vector2(coin_right-sw,160.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("cfd6dd"))'''
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("skull spacing, smaller coins, silver always on")
