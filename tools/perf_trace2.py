import io
import re

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

WRAPS = [
    ("func _spawn_zombie(", "zombie_spawn"),
    ("func _spawn_pickup(", "pickup_spawn"),
    ("func _drop_coins(", "coin_drop"),
    ("func _spawn_gate(", "gate_spawn"),
    ("func _spawn_barrel(", "barrel_spawn"),
    ("func _spawn_crate(", "crate_spawn"),
    ("func _blood_splatter(", "blood_splatter"),
    ("func _spawn_obstacle_pattern(", "obstacle_spawn"),
]

for sig, label in WRAPS:
    start = t.find(sig)
    if start < 0:
        print("missing:", sig)
        continue
    line_end = t.find("\n", start)
    body_start = line_end + 1
    # insert the timer as the first statement
    if '_pt0' in t[body_start:body_start + 200]:
        continue
    t = t[:body_start] + "\tvar _pt0 := Time.get_ticks_usec()\n" + t[body_start:]

    # find the end of the function: next "\nfunc " after body_start
    nxt = t.find("\nfunc ", body_start)
    if nxt < 0:
        nxt = len(t)
    # insert the trace right before the function's trailing blank line
    insert_at = t.rfind("\n", body_start, nxt)
    t = t[:insert_at] + '\n\t_perf_trace("%s", _pt0)\n' % label + t[insert_at:]

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("wrapped", len(WRAPS), "spawn paths with the perf timer")
