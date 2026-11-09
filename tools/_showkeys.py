import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()

for key in ("sedan", "sedan_desc", "tank", "tank_desc", "gold_car", "gold_car_desc", "cruiser", "cruiser_desc"):
    hits = re.findall(r'"%s":"([^"]*)"' % key, t)
    print(key, "->", hits[:2])
