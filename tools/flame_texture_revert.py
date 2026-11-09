import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
h = io.open(p, encoding="utf-8").read()

old = 'mat.albedo_texture = load("res://assets/vfx/flame_jet.png")'
new = 'mat.albedo_texture = load("res://assets/vfx/flame_particle.png")'

n = h.count(old)
assert n >= 1, n
h = h.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(h)
print("jet texture reverted to flame_particle.png in", n, "places")
