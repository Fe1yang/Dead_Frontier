import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) loading 24 districts inside _ready froze the first launch before a single frame was drawn
old_ready = '\t_prewarm_districts()\n\tBootTrace.mark("main: _ready start")'
if t.count(old_ready) == 1:
    t = t.replace(old_ready, '\tBootTrace.mark("main: _ready start")', 1)

# 2) one district per frame while the loading screen is up
start = t.find("func _prewarm_districts() -> void:")
end = t.find("func _district_scene(")
assert start > 0 and end > start
new_fn = '''## One district per frame. Loading all 24 in _ready froze the first launch before the first
## frame could be drawn; the loading screen now stays up until this finishes.
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
	district_cache[path] = load(path)


'''
t = t[:start] + new_fn + t[end:]

# 3) the loading tick drives it
old_tick = '''	loading_time+=delta
	loading_progress=minf(1.0,loading_time/maxf(loading_duration,0.01))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration:
		_finish_loading()'''
new_tick = '''	loading_time+=delta
	_prewarm_step()
	var prewarm_part: float = float(district_prewarm_i) / 24.0
	loading_progress = minf(0.98, maxf(loading_time/maxf(loading_duration,0.01), prewarm_part))
	# same random image from start to finish, no switching
	if loading_time>=loading_duration and districts_ready:
		_finish_loading()'''
assert t.count(old_tick) == 1, t.count(old_tick)
t = t.replace(old_tick, new_tick, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("district prewarm spread across the loading screen")
