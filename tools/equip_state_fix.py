import io

HP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
h = io.open(HP, encoding="utf-8").read()

old = '\tvar etxt: String=("已装备" if zh else "EQUIPPED") if equipped_now else ("装备" if zh else "EQUIP")'
new = '\t\tvar etxt: String=("已装备" if zh else "EQUIPPED") if equipped_now else ("装备" if zh else "EQUIP")'
assert h.count(old) == 1
h = h.replace(old, new, 1)
io.open(HP, "w", encoding="utf-8", newline="\n").write(h)

TP = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_text.gd"
t = io.open(TP, encoding="utf-8").read()
if "char_equipped" not in t:
    pairs = (
        ('"zh_CN":{', '"zh_CN":{"char_equipped":"已装备",'),
        ('"zh_TW":{', '"zh_TW":{"char_equipped":"已裝備",'),
        ('"en":{', '"en":{"char_equipped":"ALREADY EQUIPPED",'),
    )
    added = 0
    for old_k, new_k in pairs:
        if old_k in t:
            t = t.replace(old_k, new_k, 1)
            added += 1
    io.open(TP, "w", encoding="utf-8", newline="\n").write(t)
    print("toast keys added:", added)
else:
    print("toast key already present")
