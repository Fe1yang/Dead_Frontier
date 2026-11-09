import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# start every run with two molotovs so they can be tried immediately
pp = base + r"\player_3d.gd"
t = io.open(pp, encoding="utf-8").read()
if "molotov_count = 0" in t and "molotov_count = 2" not in t:
    t = t.replace("\tmolotov_count = 0", "\tmolotov_count = 2", 1)
    t = t.replace("var molotov_count := 0", "var molotov_count := 2", 1)
    io.open(pp, "w", encoding="utf-8", newline="\n").write(t)

# the grenade button throws the bottle while one is carried
mp = base + r"\main_3d.gd"
m = io.open(mp, encoding="utf-8").read()
old = '_throw_ordnance("frag")'
if old in m and 'molotov_count>0' not in m:
    m = m.replace(old, '_throw_ordnance("molotov" if player.molotov_count>0 else "frag")')
    io.open(mp, "w", encoding="utf-8", newline="\n").write(m)
    print("grenade button prefers the molotov while one is carried")
else:
    print("throw call site:", "already patched" if 'molotov_count>0' in m else "not found")
