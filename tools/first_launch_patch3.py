import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# Enter the lobby as soon as the districts that can be on screen are in; the rest keep streaming
# in during the lobby's idle frames, one per frame.
old = '''	if district_prewarm_i >= 24:
		districts_ready = true
		print("DISTRICTS_PREWARMED ", district_cache.size())
		return'''
new = '''	if district_prewarm_i >= 24:
		districts_ready = true
		return
	if district_prewarm_i >= DISTRICTS_NEEDED:
		districts_ready = true'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

if "DISTRICTS_NEEDED" not in t.split("func _prewarm_step")[0]:
    t = t.replace(
        "var district_prewarm_i := 0",
        "const DISTRICTS_NEEDED := 7   # ~110 m of street; the rest stream in from the lobby\nvar district_prewarm_i := 0",
        1,
    )

# keep streaming while the player sits in the lobby
old_idle = '\tif state!="playing": _warm_up_tick()'
new_idle = '\tif state!="playing":\n\t\t_warm_up_tick()\n\t\t_prewarm_step()'
assert t.count(old_idle) == 1, t.count(old_idle)
t = t.replace(old_idle, new_idle, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("boot needs 7 districts; the rest stream from the lobby")
