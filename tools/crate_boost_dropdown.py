import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) bigger items on the crates and barrels
cp = base + r"\weapon_crate_3d.gd"
c = io.open(cp, encoding="utf-8").read()
assert "const ITEM_BOOST := 1.7" in c
c = c.replace("const ITEM_BOOST := 1.7", "const ITEM_BOOST := 2.4", 1)
io.open(cp, "w", encoding="utf-8", newline="\n").write(c)
print("crate item boost 1.7 -> 2.4")

# 2) the equip dropdown belongs just above the cards, not up over the 3D stage
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()
old = "return Rect2(c.position.x-6.0,c.position.y-96.0,c.size.x+12.0,50.0)"
new = "return Rect2(c.position.x-6.0,c.position.y-52.0,c.size.x+12.0,46.0)"
assert m.count(old) == 1, m.count(old)
m = m.replace(old, new, 1)
io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
print("equip dropdown sits directly above the card")
