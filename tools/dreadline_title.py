import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) the title screen shows the Dreadline poster
hp = base + r"\scripts\hud.gd"
h = io.open(hp, encoding="utf-8").read()
old = 'menu_art=load("res://assets/ui/cover.png")'
new = 'menu_art=load("res://assets/ui/title_screen.png")'
assert h.count(old) == 1
h = h.replace(old, new, 1)
io.open(hp, "w", encoding="utf-8", newline="\n").write(h)
print("title screen -> Dreadline poster")

# 2) and so does the launch splash
pp = base + r"\project.godot"
p = io.open(pp, encoding="utf-8").read()
old_s = 'boot_splash/image="res://assets/ui/cover.png"'
new_s = 'boot_splash/image="res://assets/ui/title_screen.png"'
assert p.count(old_s) == 1
p = p.replace(old_s, new_s, 1)
io.open(pp, "w", encoding="utf-8", newline="\n").write(p)
print("boot splash -> Dreadline poster")
