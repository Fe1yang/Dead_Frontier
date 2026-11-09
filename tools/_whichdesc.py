import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\store_catalog.gd"
t = io.open(p, encoding="utf-8").read()

for i, line in enumerate(t.split("\n")):
    if "unlock_all_desc" not in line:
        continue
    m = re.match(r'\s*"([a-zA-Z_]{2,7})":\{', line)
    lang = m.group(1) if m else "?"
    has = ("future updates" in line) or ("今后" in line) or ("今後" in line)
    print("line", i + 1, "lang", lang, "extended", has)
