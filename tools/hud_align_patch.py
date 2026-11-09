import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# 1) flush the weapon label and the grenade/flash line to the screen edge
t = t.replace(
    '\t_text_right(weapon_label,Vector2(right_top.x+6,right_top.y+26),16,MUTED)',
    '\t_text_right(weapon_label,Vector2(RIGHT_ALIGN,right_top.y+26),16,MUTED)',
    1,
)
old_util = '\t\t_text_right("%s ×%d   %s ×%d"%[RunText.text("l_grenade"),game.player.grenade_count,RunText.text("l_flashbang"),game.player.flashbang_count],Vector2(right_top.x+6,right_top.y+50),15,MUTED)'
new_util = '\t\t_text_right("%s ×%d   %s ×%d"%[RunText.text("l_grenade"),game.player.grenade_count,RunText.text("l_flashbang"),game.player.flashbang_count],Vector2(RIGHT_ALIGN,right_top.y+50),15,MUTED)'
assert t.count(old_util) == 1
t = t.replace(old_util, new_util, 1)

# 2) coins on ONE line, right aligned to the same edge as the lines above
old = '''	# right aligned, small, both currencies always visible so the player can read the stock
	var coin_right: float=524.0
	var gw: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	draw_string(bold,Vector2(coin_right-gw,140.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("f2c14e"))
	var sw: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	draw_string(bold,Vector2(coin_right-sw,160.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("cfd6dd"))'''
new = '''	# both currencies on one line, flush with the ammo / grenade lines above
	var gold_w: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	var silver_w: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	var coin_gap: float=14.0
	var coin_total: float=gold_w+coin_gap+silver_w
	draw_string(bold,Vector2(RIGHT_ALIGN-coin_total,150.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("f2c14e"))
	draw_string(bold,Vector2(RIGHT_ALIGN-silver_w,150.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("cfd6dd"))'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

# 3) shared right edge constant
anchor = "const HEART=Color(\"a3201f\")"
t = t.replace(anchor, "## Right edge used by every top-right readout so they line up.\nconst RIGHT_ALIGN:=534.0\n" + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("right aligned HUD rows")
