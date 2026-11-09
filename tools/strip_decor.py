import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# remove the decoration call entirely: nothing is placed on the street until we add it back one
# item at a time and agree on the position.
old_call = "\n\t_decorate_district(road, i)"
assert t.count(old_call) == 1
t = t.replace(old_call, "", 1)

# stop hiding the district's own lamp posts as well
old_hide = "\n\t_hide_road_lamps(road)"
if t.count(old_hide) == 1:
    t = t.replace(old_hide, "", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("all street decoration removed; the helpers stay in the file unused")
