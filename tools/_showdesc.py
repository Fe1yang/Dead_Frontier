import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()

for m in list(re.finditer(r'"unlock_all_desc":"([^"]*)"', t))[:6]:
    print("DESC:", m.group(1)[:100])
