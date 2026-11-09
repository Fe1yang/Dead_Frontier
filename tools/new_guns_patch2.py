import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

pp = base + r"\player_3d.gd"
p = io.open(pp, encoding="utf-8").read()

if "MAKAROV" not in p:
    old_len = 'const WEAPON_LENGTHS := {"FLAME": 0.78, "PISTOL": 0.26,'
    assert p.count(old_len) == 1
    p = p.replace(old_len, 'const WEAPON_LENGTHS := {"MAKAROV": 0.26, "SUOMI": 0.72, "FLAME": 0.78, "PISTOL": 0.26,', 1)

    old_dmg = '\t\t"FLAME": return 6.0*damage_scale'
    assert p.count(old_dmg) == 1
    p = p.replace(old_dmg, '\t\t"MAKAROV": return 85.0*damage_scale\n\t\t"SUOMI": return 16.0*damage_scale\n' + old_dmg, 1)

    old_stats = '\t\t"FLAME":\n\t\t\tmagazine_size = 100;'
    assert p.count(old_stats) == 1, p.count(old_stats)
    p = p.replace(old_stats, '''		"MAKAROV":
			magazine_size = 8; damage = 85.0*damage_scale; fire_interval = 0.55*rate_scale
			bullet_speed = 44.0; pierce = 1; reload_duration = 1.45; reserve_ammo = 40
		"SUOMI":
			magazine_size = 50; damage = 16.0*damage_scale; fire_interval = 0.10*rate_scale
			bullet_speed = 30.0; pierce = 0; reload_duration = 1.55; reserve_ammo = 150
''' + old_stats, 1)

    p = p.replace('const HOLD_DROP := {"PISTOL":0.10,', 'const HOLD_DROP := {"MAKAROV":0.10,"SUOMI":0.10,"PISTOL":0.10,', 1)
    p = p.replace('const SUPPORT_REACH := {"PISTOL":0.03,', 'const SUPPORT_REACH := {"MAKAROV":0.05,"SUOMI":0.16,"PISTOL":0.03,', 1)

    io.open(pp, "w", encoding="utf-8", newline="\n").write(p)
    print("player_3d: MAKAROV + SUOMI registered")

mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()
old_pool = 'const CRATE_WEAPONS:=["SMG","SHOTGUN","SNIPER","PISTOL","LAUNCHER","RIFLE"]'
if old_pool in m:
    m = m.replace(old_pool, 'const CRATE_WEAPONS:=["SMG","SHOTGUN","SNIPER","PISTOL","LAUNCHER","RIFLE","MAKAROV","SUOMI"]', 1)
    io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
    print("main_3d: Makarov and Suomi added to the crate pool")
