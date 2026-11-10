import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# hotter jet, and a softer falloff so the middle of the cone still bites
t = t.replace("const FLAME_TICK_DAMAGE := 22.0", "const FLAME_TICK_DAMAGE := 34.0", 1)
t = t.replace("return lerpf(0.22, 1.0, pow(t, 1.4))", "return lerpf(0.34, 1.0, pow(t, 1.15))", 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("flame damage raised and falloff softened")
