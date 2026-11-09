import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# While the equip dropdown is open for a card, hide that card's name: the dropdown covers the
# portrait area and a label peeking out from under it looks broken.
old = '\t\t_text_center(label,Vector2(card.get_center().x,card.end.y-9),11 if pets else 12,WHITE if on else MUTED)'
new = ('\t\tvar menu_open: bool = game.lobby_tab==0 and int(game.equip_menu_index)==i\n'
       '\t\tif not menu_open:\n'
       '\t\t\t_text_center(label,Vector2(card.get_center().x,card.end.y-9),11 if pets else 12,WHITE if on else MUTED)')
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("card name hidden while its equip dropdown is open")
