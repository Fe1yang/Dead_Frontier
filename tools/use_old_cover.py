import io

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

h = io.open(ROOT + r"\scripts\hud.gd", encoding="utf-8").read()
h = h.replace(
    'menu_art=load("res://assets/ui/launch_cover.png")',
    'menu_art=load("res://assets/ui/title_screen_old.png")',
    1,
)
io.open(ROOT + r"\scripts\hud.gd", "w", encoding="utf-8", newline="\n").write(h)

g = io.open(ROOT + r"\project.godot", encoding="utf-8").read()
g = g.replace(
    'boot_splash/image="res://assets/ui/launch_cover.png"',
    'boot_splash/image="res://assets/ui/title_screen_old.png"',
    1,
)
io.open(ROOT + r"\project.godot", "w", encoding="utf-8", newline="\n").write(g)
print("cover and boot splash use title_screen_old.png")
