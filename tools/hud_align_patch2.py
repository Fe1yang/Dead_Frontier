import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

if "const RIGHT_ALIGN" not in t:
    anchor = 'const HEART=Color("a3201f")'
    assert t.count(anchor) == 1
    t = t.replace(anchor, '## Right edge shared by every top-right readout so the rows line up.\nconst RIGHT_ALIGN:=534.0\n' + anchor, 1)

for old, new in (
    ("_text_right(weapon_label,Vector2(right_top.x+6,right_top.y+26),16,MUTED)",
     "_text_right(weapon_label,Vector2(RIGHT_ALIGN,right_top.y+26),16,MUTED)"),
    ('_text_right("%s ×%d   %s ×%d"%[RunText.text("l_grenade"),game.player.grenade_count,RunText.text("l_flashbang"),game.player.flashbang_count],Vector2(right_top.x+6,right_top.y+48),15,MUTED)',
     '_text_right("%s ×%d   %s ×%d"%[RunText.text("l_grenade"),game.player.grenade_count,RunText.text("l_flashbang"),game.player.flashbang_count],Vector2(RIGHT_ALIGN,right_top.y+48),15,MUTED)'),
):
    assert t.count(old) == 1, old[:40]
    t = t.replace(old, new, 1)

old_coins = t[t.find("\t# right aligned, small, both currencies always visible"):]
old_coins = old_coins[:old_coins.find("\n\n")]
new_coins = """	# both currencies on one line, flush with the ammo / grenade rows above
	var gold_w: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	var silver_w: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x
	var coin_total: float=gold_w+14.0+silver_w
	draw_string(bold,Vector2(RIGHT_ALIGN-coin_total,150.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("f2c14e"))
	draw_string(bold,Vector2(RIGHT_ALIGN-silver_w,150.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("cfd6dd"))"""
assert old_coins.startswith("\t# right aligned")
t = t.replace(old_coins, new_coins, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("rows right aligned, coins on one line")
