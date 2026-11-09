import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

pairs = (
    ("const FLAME_RANGE := 9.0", "const FLAME_RANGE := 10.5"),
    ("const FLAME_HALF_ANGLE := 8.0", "const FLAME_HALF_ANGLE := 11.0"),
    ("const FLAME_BURN_SECONDS := 2.5", "const FLAME_BURN_SECONDS := 3.0"),
    ("const FLAME_BURN_FRACTION := 0.06", "const FLAME_BURN_FRACTION := 0.09"),
    ("\t\tz.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)",
     "\t\t_hit_zombie(z, FLAME_TICK_DAMAGE, \"torso\", z.position + Vector3(0, 1.0, 0), Color(\"ffb14d\"))\n"
     "\t\tz.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)"),
)

for old, new in pairs:
    assert t.count(old) == 1, old
    t = t.replace(old, new, 1)

if "FLAME_TICK_DAMAGE" not in t.split("func _fire_flame")[0]:
    t = t.replace(
        "const FLAME_BURN_FRACTION := 0.09",
        "const FLAME_BURN_FRACTION := 0.09\nconst FLAME_TICK_DAMAGE := 22.0   # per 0.12 s tick: it is a paid gold weapon",
        1,
    )

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flamethrower buffed")
