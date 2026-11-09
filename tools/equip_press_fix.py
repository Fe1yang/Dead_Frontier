import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\t\tif lobby_view_rect().has_point(pos): lobby_press=pos; lobby_dragged=false; return true"
new = (
    "\t\t# The equip dropdown lives above the card strip, outside lobby_view_rect(): without this\n"
    "\t\t# the press was never registered and the popup could not be tapped at all.\n"
    "\t\tif lobby_view_rect().has_point(pos) or (equip_menu_index>=0 and equip_menu_rect().has_point(pos)):\n"
    "\t\t\tlobby_press=pos; lobby_dragged=false; return true"
)

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("presses on the equip dropdown are registered")
