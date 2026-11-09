import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "func armory_price" not in t:
    anchor = "func armory_upgrade() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, '''## Silver cost of the next level of this weapon (0 when maxed or not sold here).
func armory_price() -> int:
	var sid := armory_shop_id()
	if sid == "":
		return 0
	for item in shop_items:
		if String(item.id) == sid:
			return item_cost(item)
	return 0


''' + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("armory_price added")
