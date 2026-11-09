import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\shop_text.gd"
t = io.open(p, encoding="utf-8").read()

pairs = (
    ('"n_launcher":"榴弹发射器"', '"n_launcher":"榴弹发射器","n_flame":"火焰喷射器"'),
    ('"n_launcher":"榴彈發射器"', '"n_launcher":"榴彈發射器","n_flame":"火焰噴射器"'),
    ('"n_launcher":"GRENADE LAUNCHER"', '"n_launcher":"GRENADE LAUNCHER","n_flame":"FLAMETHROWER"'),
)

added = 0
for old, new in pairs:
    if old in t:
        t = t.replace(old, new, 1)
        added += 1

if "n_flame" not in t:
    t = t.replace('"n_shotgun":"SHOTGUN"', '"n_shotgun":"SHOTGUN","n_flame":"FLAMETHROWER"', 1)
    added += 1

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("blocks patched:", added, "has n_flame:", "n_flame" in t)
