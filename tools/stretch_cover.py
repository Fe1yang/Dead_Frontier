import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\project.godot"
t = io.open(p, encoding="utf-8").read()

# "fill the height, crop the sides" is keep_height
t = t.replace('window/stretch/aspect="expand"', 'window/stretch/aspect="keep_height"', 1)

if "boot_splash/fullsize" not in t:
    old = 'boot_splash/image="res://assets/ui/cover.png"'
    new = old + "\nboot_splash/fullsize=true\nboot_splash/use_filter=true"
    assert t.count(old) == 1
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("aspect keep_height; splash full size")
