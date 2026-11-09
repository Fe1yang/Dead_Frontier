import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "molotov_count" not in t:
    old = "var flashbang_count := 1"
    assert t.count(old) == 1
    t = t.replace(old, old + "\nvar molotov_count := 0", 1)

    old2 = "\tgrenade_count = 2"
    assert t.count(old2) == 1
    t = t.replace(old2, "\tgrenade_count = 2\n\tmolotov_count = 0", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("molotov_count added")
else:
    print("molotov_count already present")
