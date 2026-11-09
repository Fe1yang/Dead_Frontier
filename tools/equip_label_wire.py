import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(P, encoding="utf-8").read()

old = '\t\tvar zh: bool=String(game.language_code).begins_with("zh")\n\t\tvar etxt: String=("已装备" if zh else "EQUIPPED") if equipped_now else ("装备" if zh else "EQUIP")'
new = (
    '\t\tvar etxt: String = ShopText.text(game.language_code, "char_equipped" if equipped_now else "btn_equip")'
)
assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(h)
print("dropdown label now comes from the 20-language table")
