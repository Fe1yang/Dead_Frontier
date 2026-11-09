import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# vouchers are endless too
t = t.replace(
    'bold.get_string_size(_compact(game.bank_vouchers),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x)',
    'bold.get_string_size("∞" if game.infinite_resources() else _compact(game.bank_vouchers),HORIZONTAL_ALIGNMENT_LEFT,-1,_scaled(ts)).x)',
)
t = t.replace(
    'var vouchers:=_compact(game.bank_vouchers)',
    'var vouchers:=("∞" if infw else _compact(game.bank_vouchers))',
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("vouchers show the infinity mark")
