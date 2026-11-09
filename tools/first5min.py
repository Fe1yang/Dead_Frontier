import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# prime the audio once, the moment loading starts
old = "\tvar frames := 0"
if t.count("sound.prime_all()") == 0:
    anchor = "func _finish_loading() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor, 1)

# threaded prewarm: request the district scenes up front, poll them as the bar advances
old_pre = '''	var path: String = "res://assets/models/environment/city_hd_%02d.glb" % district_prewarm_i
	district_prewarm_i += 1
	if not ResourceLoader.exists(path):
		return
	if district_cache.has(path):
		return
	district_cache[path] = load(path)'''
new_pre = '''	var path: String = "res://assets/models/environment/city_hd_%02d.glb" % district_prewarm_i
	district_prewarm_i += 1
	if not ResourceLoader.exists(path):
		return
	if district_cache.has(path):
		return
	# On a worker thread: parsing a 10 MB district on the main thread is exactly the hitch that
	# showed up as soon as the bar finished.
	if not _district_requests.has(path):
		if ResourceLoader.load_threaded_request(path) == OK:
			_district_requests[path] = 0
		else:
			district_cache[path] = load(path)
		return
	if ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_LOADED:
		var packed: Resource = ResourceLoader.load_threaded_get(path)
		if packed != null:
			district_cache[path] = packed
		_district_requests.erase(path)'''
assert t.count(old_pre) == 1, t.count(old_pre)
t = t.replace(old_pre, new_pre, 1)

# and the loading screen waits for them instead of dropping into a cold run
old_ready = '''	if district_prewarm_i >= DISTRICTS_NEEDED:
		districts_ready = true'''
new_ready = '''	if district_prewarm_i >= DISTRICTS_NEEDED:
		# only declare the world ready once every requested district is actually in memory
		if _district_requests.is_empty():
			districts_ready = true
		return'''
assert t.count(old_ready) == 1, t.count(old_ready)
t = t.replace(old_ready, new_ready, 1)

# prime audio at the start of a run (first sound otherwise decodes mid-fight)
old_begin = "func _begin_loading(state_name: String) -> void:"
if t.count(old_begin) == 1 and "sound.prime_all()" not in t:
    t = t.replace(old_begin, old_begin + "\n\tif sound != null:\n\t\tsound.prime_all()", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("loading prewarms districts on threads and primes audio")
