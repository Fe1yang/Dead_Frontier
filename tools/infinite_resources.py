import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) the flag lives on main: "unlock all" means the wallet is bottomless
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()
if "func infinite_resources" not in m:
    anchor = "func _grant(coins: int,vouchers: int) -> void:"
    assert m.count(anchor) == 1
    helper = '''## Bought "unlock all": coins, silver, vouchers and cans are endless, shown as the infinity mark.
func infinite_resources() -> bool:
	return all_access


'''
    m = m.replace(anchor, helper + anchor, 1)
    io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
    print("infinite_resources() added")

# 2) never charge a run out of a bottomless tank
sp = base + r"\stamina_system.gd"
s = io.open(sp, encoding="utf-8").read()
if "infinite" not in s:
    old = '''func consume() -> bool:
	refresh(false)
	if value<RUN_COST: return false'''
    new = '''var infinite := false   # set by main when the player owns "unlock all"


func consume() -> bool:
	refresh(false)
	if infinite:
		return true
	if value<RUN_COST: return false'''
    assert s.count(old) == 1
    s = s.replace(old, new, 1)
    io.open(sp, "w", encoding="utf-8", newline="\n").write(s)
    print("stamina honours the infinite flag")

# 3) the wallet prints the infinity sign
hp = base + r"\hud.gd"
h = io.open(hp, encoding="utf-8").read()
old_w = '''	var cans: String="%d/%d"%[game.stamina.value,game.stamina.CAP]'''
new_w = '''	var inf: bool=game.infinite_resources()
	var cans: String="\\\\u221e" if inf else "%d/%d"%[game.stamina.value,game.stamina.CAP]'''
if old_w in h and "game.infinite_resources()" not in h:
    h = h.replace(old_w, new_w, 1)
    h = h.replace('bold.get_string_size(_compact(game.bank_coins),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x',
                  'bold.get_string_size("\\\\u221e" if inf else _compact(game.bank_coins),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x', 1)
    h = h.replace('bold.get_string_size(_compact(game.bank_silver),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x',
                  'bold.get_string_size("\\\\u221e" if inf else _compact(game.bank_silver),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x', 1)
    io.open(hp, "w", encoding="utf-8", newline="\n").write(h)
    print("wallet prints the infinity mark")
