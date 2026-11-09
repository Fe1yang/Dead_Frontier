import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\project.godot"
t = io.open(p, encoding="utf-8").read()

add = (
    'boot_splash/show_image=true\n'
    'boot_splash/fullsize=true\n'
    'boot_splash/use_filter=true\n'
)

if "boot_splash/show_image" not in t:
    anchor = 'boot_splash/image="res://assets/ui/title_screen.png"\n'
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + add, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("boot splash pinned to the game cover, fullscreen")
else:
    print("boot splash keys already present")
