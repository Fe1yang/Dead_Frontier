import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# While the dropdown is open it swallows the tap: the tab under it must not fire.
old = "\t\tequip_menu_index=-1  # tapping elsewhere closes the dropdown"
new = "\t\tequip_menu_index=-1  # tapping elsewhere just closes the dropdown\n\t\treturn              # and the tap goes no further"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("dropdown swallows the tap so the buttons under it are dead")
