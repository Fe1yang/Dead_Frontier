import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old_local = "\tvar world_speed: float=(3.5*(player.effective_move_mult() if state==\"playing\" else 1.0)) if state in"
idx = t.find(old_local)
assert idx > 0
line_end = t.find("\n", idx)
line = t[idx:line_end]
new_line = line.replace("\tvar world_speed: float=", "\tworld_speed=", 1)
t = t[:idx] + new_line + t[line_end:]

if "var world_speed" not in t:
    anchor = "var vehicle_auto_active:=false"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + "\n## Road scroll speed for this frame; barrels and crates ride the same number.\nvar world_speed:=3.5", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("world_speed promoted to a member")
