import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

anchor = "func _build_road() -> void:"
assert t.count(anchor) == 1

cache = '''## District scenes are loaded once at startup: loading them inside _build_road was the single
## biggest frame spike of a run (24 models, about 4 MB each, decoded on the first frame).
var district_cache := {}


func _prewarm_districts() -> void:
	for i in range(24):
		var path: String = "res://assets/models/environment/city_hd_%02d.glb" % i
		if not ResourceLoader.exists(path):
			continue
		if district_cache.has(path):
			continue
		district_cache[path] = load(path)
	print("DISTRICTS_PREWARMED ", district_cache.size())


func _district_scene(path: String) -> Resource:
	if district_cache.has(path):
		return district_cache[path]
	var packed: Resource = load(path) if ResourceLoader.exists(path) else null
	if packed != null:
		district_cache[path] = packed
	return packed


'''

t = t.replace(anchor, cache + anchor, 1)

old = "\t\tvar packed: Resource=load(path)"
new = "\t\tvar packed: Resource=_district_scene(path)"
assert t.count(old) == 1
t = t.replace(old, new, 1)

old2 = "func _ready() -> void:"
new2 = "func _ready() -> void:\n\t_prewarm_districts()"
assert t.count(old2) == 1
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("district prewarm added")
