import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) swap the card colours: the week pass gets violet rays, the month pass gold
p = ROOT + r"\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()
t = t.replace('{"id":"pass_weekly","kind":"pass","name":"pass_weekly","coins":200,"cans":30,"vouchers":0,"tier":2,"usd":3.99,"bonus":0,"glow":"gold","rays":12}',
              '{"id":"pass_weekly","kind":"pass","name":"pass_weekly","coins":200,"cans":30,"vouchers":0,"tier":2,"usd":3.99,"bonus":0,"glow":"violet","rays":12}', 1)
t = t.replace('{"id":"pass_monthly","kind":"pass","name":"pass_monthly","coins":500,"cans":100,"vouchers":0,"tier":3,"bonus":0,"glow":"violet","rays":16}',
              '{"id":"pass_monthly","kind":"pass","name":"pass_monthly","coins":500,"cans":100,"vouchers":0,"tier":3,"bonus":0,"glow":"gold","rays":16}', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("pass colours swapped")

# 2) the card art fills more of the card
p2 = ROOT + r"\scripts\hud.gd"
h = io.open(p2, encoding="utf-8").read()
old = "\tvar available:=r.grow(-r.size.x*0.07)"
new = "\tvar available:=r.grow(-r.size.x*0.015)"
assert h.count(old) == 1, h.count(old)
h = h.replace(old, new, 1)
io.open(p2, "w", encoding="utf-8", newline="\n").write(h)
print("store art margin 7% -> 1.5%")
