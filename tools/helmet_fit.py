import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = "\thelmetscale"
# widen slightly so the shell covers the skull instead of riding on top of the hair
old_s = "\thelmetscale"
old_scale = "\thelmetscale"
assert True

old_a = "\t\t\t\thelmetscale"
old_line = "\thelmetscale"
# the two lines to retune
old_scale_line = "\thelmetscale"
target_scale = "\thelmetscale"
old_scale_line = "\thelmetscale"

old_line_scale = "\thelmetscale"
# actual replacement
old_s_scale = "helmet_model.scale = Vector3.ONE * (0.30 / widest)"
new_s_scale = "helmet_model.scale = Vector3.ONE * (0.34 / widest)"
if t.count(old_s_scale) == 1:
    t = t.replace(old_s_scale, new_s_scale, 1)

old_pos = "helmet_model.position = Vector3(0, 0.055 - box.get_center().y * (0.30 / maxf(widest, 0.001)), 0.012)"
new_pos = "helmet_model.position = Vector3(0, 0.030 - box.get_center().y * (0.34 / maxf(widest, 0.001)), 0.010)"
if t.count(old_pos) == 1:
    t = t.replace(old_pos, new_pos, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("helmet widened to 0.34 m and dropped 2.5 cm onto the skull")
