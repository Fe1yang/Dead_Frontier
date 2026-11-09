import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) the 24 districts were loaded synchronously inside _ready, which is the freeze on first launch:
#    no frame is drawn until every model and its 2048 texture is in memory.
old_ready = "\t_prewarm_districts()\n\tBootTrace.mark(\"main: _ready start\")"
new_ready = "\tBootTrace.mark(\"main: _ready start\")"
assert t.count(old_ready) == 1
t = t.replace(old_ready, new_ready, 1)

# 2) spread it across frames while the loading screen is up
old_prewarm = '''func _prewarm_districts() -> void:
	for i in range(24):
		var path: String = "res://assets/models/environment/city_hd_%02d.glb" % i
		if not ResourceLoader.exists(path): continue
		if district_cache.has(path): continue
		district_cache[path] = load(path)
	print("DISTRICTS_PREWARMED ", district_cache.size())'''
new_prewarm = '''## One district per frame: loading all 24 in _ready froze the first launch before the first
## frame could be drawn. The loading screen stays up until this finishes.
var district_prewarm_i := 0
var districts_ready := false


func _prewarm_step() -> void:
	if districts_ready:
		return
	if district_prewarm_i >= 24:
		districts_ready = true
		print("DISTRICTS_PREWARMED ", district_cache.size())
		return
	var path: String = "res://assets/models/environment/city_hd_%02d.glb" % district_prewarm_i
	district_prewarm_i += 1
	if not ResourceLoader.exists(path):
		return
	if district_cache.has(path):
		return
	district_cache[path] = load(path)'''
assert t.count(old_prewarm) == 1, t.count(old_prewarm)
t = t.replace(old_prewarm, new_prewarm, 1)

# 3) the loading tick drives the prewarm and only finishes when the districts are in
old_tick = '''func _tick_loading(delta: float) -> void:
	loading_time+=delta
	loading_progress=minf(1.0,loading_time/maxf(loading_duration,0.01))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration:
		_finish_loading()'''
new_tick = '''func _tick_loading(delta: float) -> void:
	loading_time+=delta
	_prewarm_step()
	var prewarm_part: float = float(district_prewarm_i) / 24.0
	loading_progress = minf(0.98, maxf(loading_time/maxf(loading_duration,0.01), prewarm_part))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration and districts_ready:
		_finish_loading()'''
assert t.count(old_tick) == 1
t = t.replace(old_tick, new_tick, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("district prewarm spread across loading frames")
