import subprocess
import os
import io

clone = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup"
target = os.path.join(clone, "assets", "ui", "cover.png")

# the poster with TAP ANYWHERE TO START baked in, deleted back in 2a7cff2
data = subprocess.run(
    ["git", "-C", clone, "show", "2a7cff2~1:assets/ui/title_screen_old.png"],
    capture_output=True,
).stdout
assert data[:4] == b"\x89PNG", data[:8]
open(target, "wb").write(data)
print("cover.png restored:", len(data), "bytes")

h = io.open(os.path.join(clone, "scripts", "hud.gd"), encoding="utf-8").read()
h = h.replace('menu_art=load("res://assets/ui/title_screen_old.png")', 'menu_art=load("res://assets/ui/cover.png")')
h = h.replace('menu_art=load("res://assets/ui/launch_cover.png")', 'menu_art=load("res://assets/ui/cover.png")')
io.open(os.path.join(clone, "scripts", "hud.gd"), "w", encoding="utf-8", newline="\n").write(h)

g = io.open(os.path.join(clone, "project.godot"), encoding="utf-8").read()
for old in ('boot_splash/image="res://assets/ui/title_screen_old.png"', 'boot_splash/image="res://assets/ui/launch_cover.png"'):
    g = g.replace(old, 'boot_splash/image="res://assets/ui/cover.png"')
io.open(os.path.join(clone, "project.godot"), "w", encoding="utf-8", newline="\n").write(g)
print("hud and project point at cover.png")
