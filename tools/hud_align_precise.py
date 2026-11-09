import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")

# right edge shared by every top-right readout
RIGHT_EDGE = 534.0

for i, line in enumerate(lines):
    # the weapon label and the grenade/flash line must sit flush at the screen edge
    if line.startswith("\t_text_right(weapon_label,Vector2(right_top.x+6,right_top.y+26)"):
        lines[i] = line.replace("Vector2(right_top.x+6,right_top.y+26)", "Vector2(%f,right_top.y+26)" % RIGHT_EDGE)
    elif line.startswith("\t\t_text_right(\"%s ×%d   %s ×%d\"") and "right_top.x+6,right_top.y+48" in line:
        lines[i] = line.replace("Vector2(right_top.x+6,right_top.y+48)", "Vector2(%f,right_top.y+48)" % RIGHT_EDGE)

# coins: both currencies on ONE line, right aligned to the same edge
coin_start = None
coin_end = None
for i, line in enumerate(lines):
    if line.strip().startswith("var coin_right: float="):
        coin_start = i
    if line.strip().startswith('draw_string(bold,Vector2(coin_right-sw,160.0)'):
        coin_end = i
assert coin_start is not None and coin_end is not None and coin_end > coin_start

new_block = [
    "\tvar gold_w: float=bold.get_string_size(gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x",
    "\tvar silver_w: float=bold.get_string_size(silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15).x",
    "\tvar coin_total: float=gold_w+14.0+silver_w",
    "\tdraw_string(bold,Vector2(%f-coin_total,150.0),gold_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color(\"f2c14e\"))" % RIGHT_EDGE,
    "\tdraw_string(bold,Vector2(%f-silver_w,150.0),silver_txt,HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color(\"cfd6dd\"))" % RIGHT_EDGE,
]
lines[coin_start:coin_end + 1] = new_block

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("coins on one line, rows flush right")
