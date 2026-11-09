import io

base = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts"

# ---------- 1) keep districts loading in the background while playing ----------
p = base + r"\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "_district_requests" not in t:
    anchor = "var district_cache:={}"
    if t.count(anchor) != 1:
        anchor = "var district_cache := {}"
    assert t.count(anchor) == 1, "district_cache declaration not found"
    t = t.replace(anchor, anchor + "\nvar _district_requests:={}   # path -> ResourceLoader threaded status", 1)

if "func _district_threads" not in t:
    helper = '''## Load the next districts on a worker thread while the player is running, so a new block never
## has to be parsed on the frame it appears (that is the hitching the phone shows).
func _district_threads() -> void:
	if player == null:
		return
	var want: int = clampi(roads.size() + 1, 0, 23)
	for k in range(3):
		var idx: int = (want + k) % 24
		var path: String = "res://assets/models/environment/city_hd_%02d.glb" % idx
		if district_cache.has(path) or _district_requests.has(path):
			continue
		if ResourceLoader.load_threaded_request(path) == OK:
			_district_requests[path] = 0
	# poll whatever is in flight
	for path in _district_requests.keys():
		var status: int = ResourceLoader.load_threaded_get_status(path)
		if status == ResourceLoader.THREAD_LOAD_LOADED:
			var packed: Resource = ResourceLoader.load_threaded_get(path)
			if packed != null:
				district_cache[path] = packed
			_district_requests.erase(path)
		elif status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
			_district_requests.erase(path)


'''
    anchor2 = "func _district_scene(path: String) -> Resource:"
    assert t.count(anchor2) == 1
    t = t.replace(anchor2, helper + anchor2, 1)

# pump it every frame of a run
if "_district_threads()" not in t.split("func _district_threads()")[0][-4000:]:
    tick_anchor = "\tbarrel_timer-=delta"
    assert t.count(tick_anchor) == 1
    t = t.replace(tick_anchor, "\t_district_threads()\n" + tick_anchor, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("districts now stream in on worker threads")

# ---------- 2) prime every audio stream so the first shot never decodes mid-run ----------
sp = base + r"\sound.gd"
s = io.open(sp, encoding="utf-8").read()

if "func prime_all" not in s:
    helper2 = '''## Touch every stream once at loader time: the first real playback then has nothing left to
## decode, which on iOS used to cost a frame right in the middle of a fight.
func prime_all() -> void:
	for id in streams.keys():
		var st: AudioStream = streams[id]
		if st == null:
			continue
		st.get_length()


'''
    anchor3 = "func play("
    assert s.count(anchor3) == 1
    s = s.replace(anchor3, helper2 + anchor3, 1)

io.open(sp, "w", encoding="utf-8", newline="\n").write(s)
print("sound has a prime_all hook")
