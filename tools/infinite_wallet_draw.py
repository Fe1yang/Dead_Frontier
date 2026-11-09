import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\hud.gd"
t = io.open(p, encoding="utf-8").read()

# every place the wallet prints a number honours the bottomless flag
t = t.replace(
    'var cans: String="%d/%d"%[game.stamina.value,game.stamina.CAP]',
    'var cans: String="∞" if game.infinite_resources() else "%d/%d"%[game.stamina.value,game.stamina.CAP]',
)
t = t.replace(
    'var coins:=_compact(game.bank_coins); var silver:=_compact(game.bank_silver); var vouchers:=_compact(game.bank_vouchers)',
    'var infw:=game.infinite_resources()\n\tvar coins:=("∞" if infw else _compact(game.bank_coins)); var silver:=("∞" if infw else _compact(game.bank_silver)); var vouchers:=_compact(game.bank_vouchers)',
)
t = t.replace(
    'var coins:=_compact(game.bank_coins); var silver:=_compact(game.bank_silver)',
    'var infw2:=game.infinite_resources()\n\tvar coins:=("∞" if infw2 else _compact(game.bank_coins)); var silver:=("∞" if infw2 else _compact(game.bank_silver))',
)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("wallet values honour the flag")
