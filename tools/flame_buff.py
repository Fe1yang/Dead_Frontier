import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The paid flamethrower only tickled: the burn alone was 15% of a walker's health. Give it direct
# damage per tick (it fires every 0.12 s) and a burn that actually finishes the horde.
old = "\t\t\tz.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)\n\t\t\thit += 1"
new = "\t\t\t_hit_zombie(z, FLAME_TICK_DAMAGE, \"torso\", z.position + Vector3(0, 1.0, 0), Color(\"ffb14d\"))\n\t\t\tz.ignite(FLAME_BURN_SECONDS, z.max_health * FLAME_BURN_FRACTION)\n\t\t\thit += 1"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# numbers: 0.12 s per tick, so 22 per tick is ~183 dps on the first target, burn adds ~9%/s
old_consts = """const FLAME_RANGE := 9.0
const FLAME_HALF_ANGLE := 8.0
const FLAME_BURN_SECONDS := 2.5
const FLAME_BURN_FRACTION := 0.06"""
new_consts = """const FLAME_RANGE := 10.5
const FLAME_HALF_ANGLE := 11.0
const FLAME_BURN_SECONDS := 3.0
const FLAME_BURN_FRACTION := 0.09
const FLAME_TICK_DAMAGE := 22.0"""
assert t.count(old_consts) == 1, t.count(old_consts)
t = t.replace(old_consts, new_consts, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("flamethrower buffed: 22 direct per tick, 9%/s burn, 10.5 m, 11 deg")
