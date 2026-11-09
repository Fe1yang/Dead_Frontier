import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# 1) real infinity glyph instead of an escaped one
hp = base + r"\hud.gd"
h = io.open(hp, encoding="utf-8").read()
h = h.replace('"\\\\u221e"', '"∞"')
io.open(hp, "w", encoding="utf-8", newline="\n").write(h)
print("glyph fixed:", '"∞"' in h)

# 2) switch the tank to endless whenever all_access is on
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()

if "stamina.infinite = all_access" not in m:
    old = "\t\t\tall_access=true; remove_ads=true"
    new = "\t\t\tall_access=true; remove_ads=true\n\t\t\tstamina.infinite=true"
    assert m.count(old) == 1
    m = m.replace(old, new, 1)

    # returning players who already own it
    anchor = "func infinite_resources() -> bool:\n\treturn all_access"
    assert m.count(anchor) == 1
    m = m.replace(anchor, anchor, 1)

io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
print("stamina.infinite wired to all_access")
