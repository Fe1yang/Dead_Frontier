import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# 1) the dropdown was drawn BEFORE the tabs, so the tab labels painted over it
block_start = t.find("\t# dropdown over a survivor card: tap it to wear them")
assert block_start > 0
block_end = t.find("\t# Main screen. The 3D survivor and pet stand in the middle", block_start)
assert block_end > block_start
block = t[block_start:block_end]
t = t[:block_start] + t[block_end:]

# draw it at the very end of the lobby screen instead
helper = "func _draw_equip_menu() -> void:\n" + block.replace(
    "if game.lobby_tab==0 and int(game.equip_menu_index)>=0:",
    "if game.lobby_tab==0 and int(game.equip_menu_index)>=0:", 1)
t = t.replace("func _draw_character_select() -> void:", helper + "\n\nfunc _draw_character_select() -> void:", 1)

# find the end of _draw_character_select to append the call
start = t.find("func _draw_character_select() -> void:")
nxt = t.find("\nfunc ", start + 10)
body = t[start:nxt]
if "_draw_equip_menu()" not in body:
    body = body.rstrip("\n") + "\n\t_draw_equip_menu()\n"
    t = t[:start] + body + t[nxt:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("equip dropdown drawn last, on top of the tabs")
