import io
import shutil

# 1) real structural damage from the flame cone
p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old_const = "const FLAME_TICK_DAMAGE := 22.0   # per 0.12 s tick: it is a paid gold weapon"
assert t.count(old_const) == 1
t = t.replace(
    old_const,
    old_const + "\n## Crates and barrels count hits, not health; the flame takes several per tick.\nconst FLAME_STRUCTURE_HITS := 3",
    1,
)

old_crate = "\t\tcrate.take_hit()"
assert t.count(old_crate) == 1
t = t.replace(old_crate, "\t\tcrate.take_hit(FLAME_STRUCTURE_HITS)", 1)

old_barrel = "\t\tbarrel.take_hit()"
assert t.count(old_barrel) == 1
t = t.replace(old_barrel, "\t\tbarrel.take_hit(FLAME_STRUCTURE_HITS * 8.0)", 1)

# 2) a real flame sprite for the jet instead of the white blob
old_tex = '\tmat.albedo_texture = load("res://assets/vfx/flame_particle.png")'
if t.count(old_tex):
    pass
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flame structure damage wired")

pp = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\player_3d.gd"
h = io.open(pp, encoding="utf-8").read()
old = 'mat.albedo_texture = load("res://assets/vfx/flame_particle.png")'
if h.count(old) >= 1:
    h = h.replace(old, 'mat.albedo_texture = load("res://assets/vfx/flame_jet.png")')
    io.open(pp, "w", encoding="utf-8", newline="\n").write(h)
    print("jet now uses flame_jet.png")

src = r"C:\Users\user\AppData\Local\Temp\vfxbundle\brackeys_vfx_bundle\particles\alpha\flame_04_a.png"
dst = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\assets\vfx\flame_jet.png"
shutil.copyfile(src, dst)
print("flame_jet.png copied from the bundle")
