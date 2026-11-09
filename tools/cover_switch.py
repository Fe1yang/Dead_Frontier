import io
import re

ROOT = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"

# 1) cover art now carries the baked prompt, so the drawn pill goes away
h = io.open(ROOT + r"\scripts\hud.gd", encoding="utf-8").read()
start = h.find("\t# The prompt is part of the cover")
end = h.find("func _draw_loading()")
assert start > 0 and end > start
h = h[:start] + h[end:]

h = h.replace(
    'menu_art=load("res://assets/ui/title_screen.png")',
    'menu_art=load("res://assets/ui/launch_cover.png")',
    1,
)
io.open(ROOT + r"\scripts\hud.gd", "w", encoding="utf-8", newline="\n").write(h)

# 2) the boot splash shows the same image, prompt included
p = ROOT + r"\project.godot"
g = io.open(p, encoding="utf-8").read()
g = g.replace(
    'boot_splash/image="res://assets/ui/title_screen.png"',
    'boot_splash/image="res://assets/ui/launch_cover.png"',
    1,
)
io.open(p, "w", encoding="utf-8", newline="\n").write(g)
print("cover and boot splash both use launch_cover.png")
