import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# The lobby never shows a district, so the boot screen must not wait for them: only a run does.
old = '''	loading_time+=delta
	_prewarm_step()
	var prewarm_part: float = float(district_prewarm_i) / 24.0
	loading_progress = minf(0.98, maxf(loading_time/maxf(loading_duration,0.01), prewarm_part))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration and districts_ready:
		_finish_loading()'''
new = '''	loading_time+=delta
	if loading_target=="run":
		_prewarm_step()
		districts_ready = district_prewarm_i>=DISTRICTS_NEEDED
	else:
		# the lobby needs no street: never make the player wait for one
		districts_ready = true
	var prewarm_part: float = float(mini(district_prewarm_i, DISTRICTS_NEEDED)) / float(DISTRICTS_NEEDED)
	loading_progress = minf(0.98, maxf(loading_time/maxf(loading_duration,0.01), prewarm_part if loading_target=="run" else 0.0))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration and districts_ready:
		_finish_loading()'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("lobby boot no longer waits for districts")
