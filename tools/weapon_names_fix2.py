import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) n_flame was only in English and Simplified Chinese; add the rest
p = ROOT + r"\scripts\shop_text.gd"
lines = io.open(p, encoding="utf-8").read().split("\n")
added = 0
for i, line in enumerate(lines):
    if '{"' in line and '"n_suomi"' in line and '"n_flame"' not in line:
        lines[i] = line.replace('"n_suomi":"SUOMI",', '"n_flame":"FLAMETHROWER","n_suomi":"SUOMI",', 1)
        added += 1
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("n_flame added to", added, "blocks")

# 2) crate / barrel floating labels need the three new guns as well
p2 = ROOT + r"\scripts\weapon_crate_3d.gd"
t = io.open(p2, encoding="utf-8").read()
if '"SUOMI":"SUOMI"' not in t:
    old = '"FUEL":"FUEL: REFILL"'
    assert t.count(old) == 1, t.count(old)
    t = t.replace(old, '"FUEL":"FUEL: REFILL","SUOMI":"SUOMI","MAKAROV":"MAKAROV","FLAME":"FLAMETHROWER"', 1)
    io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
    print("crate labels added for SUOMI / MAKAROV / FLAME")
