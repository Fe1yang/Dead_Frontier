import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "func _profile_tick" not in t:
    helper = '''## Temporary hitch hunter (debug builds only): prints any tick slice that blows past 120 ms.
func _profile_tick(name: String, t0: int) -> void:
	var ms := float(Time.get_ticks_usec() - t0) / 1000.0
	if ms > 120.0 and OS.is_debug_build():
		print("HITCH ", name, " ", snappedf(ms, 0.1), " ms")


'''
    anchor = "func _menu_zombies() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

old = "\t_tick_bullets(delta); _tick_ordnance(delta); _tick_barrels(delta); _tick_crates(delta); _tick_dying_zombies(delta); _vehicle_smash(); _tick"
idx = t.find(old)
assert idx > 0
line_end = t.find("\n", idx)
line = t[idx:line_end].strip()

pieces = [pc.strip() for pc in line.split("; ") if pc.strip()]
out = []
for i, pc in enumerate(pieces):
    out.append("\tvar _t%d := Time.get_ticks_usec(); %s; _profile_tick(\"%s\", _t%d)" % (i, pc, pc[:34], i))
t = t[:idx] + "\n".join(out) + t[line_end:]

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("hitch profiler installed around", len(pieces), "tick calls")
