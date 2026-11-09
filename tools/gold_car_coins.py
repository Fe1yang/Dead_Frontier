import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = 'var as_gold: bool=(zombie_kind in GOLD_COIN_KINDS) or (is_instance_valid(player) and player.vehicle=="GOLD")'
new = 'var as_gold: bool=(zombie_kind in GOLD_COIN_KINDS) or (is_instance_valid(player) and player.vehicle in ["GOLD","GOLD_CAR"])'
assert t.count(old) == 1
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("gold car drops gold coins on every kill")
