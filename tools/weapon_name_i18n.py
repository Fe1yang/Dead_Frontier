import io
import re

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_text.gd"
t = io.open(p, encoding="utf-8").read()

# weapon names are proper nouns, so the same string works in every language
insert = '"n_suomi":"SUOMI","n_makarov":"MAKAROV",'

added = 0
lines = t.split("\n")
for i, line in enumerate(lines):
    if line.lstrip().startswith('"') and '{"btn_equip"' in line or ('"char_equipped"' in line and '{"' in line):
        if '"n_suomi"' in line:
            continue
        # place right after the opening object brace
        brace = line.find("{")
        if brace < 0:
            continue
        lines[i] = line[:brace + 1] + insert + line[brace + 1:]
        added += 1

t = "\n".join(lines)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("language blocks patched:", added)
