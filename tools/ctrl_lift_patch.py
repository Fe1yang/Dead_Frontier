import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "CTRL_LIFT" not in t:
    anchor = "const BTN_RADIUS:=36.0"
    assert t.count(anchor) == 1
    t = t.replace(
        anchor,
        "const BTN_RADIUS:=36.0\n"
        "## Every touch control sits this many pixels higher than the raw corner layout, so the\n"
        "## thumbs rest on the screen edge instead of having to hook under the buttons.\n"
        "const CTRL_LIFT:=64.0",
        1,
    )

old_sticks = (
    '\t\t"stick_left": Vector2(110,ui_h-146),\n'
    '\t\t"stick_right": Vector2(430,ui_h-146),'
)
new_sticks = (
    '\t\t"stick_left": Vector2(110,ui_h-146-CTRL_LIFT),\n'
    '\t\t"stick_right": Vector2(430,ui_h-146-CTRL_LIFT),'
)
assert t.count(old_sticks) == 1
t = t.replace(old_sticks, new_sticks, 1)

for key in ("btn_reload", "btn_swap", "btn_frag", "btn_flash", "btn_fire"):
    old = '"%s": %s+Vector2(0,dy),' % (key, "BTN_" + key.replace("btn_", "").upper())
    new = '"%s": %s+Vector2(0,dy-CTRL_LIFT),' % (key, "BTN_" + key.replace("btn_", "").upper())
    assert t.count(old) == 1, key
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("touch controls lifted by 64 px")
