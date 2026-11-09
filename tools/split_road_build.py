import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# --- 1) split the road build so a run can spread it over the loading screen ----------------
start = t.find("func _build_road() -> void:")
end = t.find("func _setup_streetlamp(")
assert start > 0 and end > start

new_block = '''## One district. Pulled out of _build_road so the run's loading screen can build them one per
## frame instead of stalling a single frame with all 24 (~255 ms, several seconds on a phone).
func _build_district(i: int) -> void:
	var asset: String="city_hd_%02d"%(i%24)
	var path: String="res://assets/models/environment/"+asset+".glb"
	if not ResourceLoader.exists(path): path="res://assets/models/environment/city_hd_00.glb"
	var packed: Resource=_district_scene(path)
	if packed==null:
		push_warning("district failed to load: "+path+" -- falling back to city_hd_00")
		packed=load("res://assets/models/environment/city_hd_00.glb")
	if packed==null:
		push_error("no district model available at all, skipping this segment")
		return
	var road:=packed.instantiate() as Node3D
	if road==null:
		push_error("district instantiate failed: "+path)
		return
	road.position=Vector3(0,0,ROAD_BEHIND-i*ROAD_SEGMENT); add_child(road)
	EnvironmentMaterials.apply(road,i); DisasterDressing.apply(road,i,ZombieScript); roads.append(road)
	_apply_cull_range(road)
	_randomize_zebra(road)
	_setup_streetlamp(road,i)
	if road.has_meta("watcher"): watchers.append(road.get_meta("watcher"))


## Builds whatever is still missing. Called once at startup; a run normally arrives here with the
## street already standing.
func _build_road() -> void:
	for i in range(roads.size(), ROAD_COUNT):
		_build_district(i)


'''
t = t[:start] + new_block + t[end:]

# --- 2) the run's loading screen builds the street one district per frame --------------------
old_tick = '''	loading_time+=delta
	if loading_target=="run":
		_prewarm_step()
		districts_ready = district_prewarm_i>=DISTRICTS_NEEDED'''
new_tick = '''	loading_time+=delta
	if loading_target=="run":
		_prewarm_step()
		if roads.size()<ROAD_COUNT:
			_build_district(roads.size())
		districts_ready = district_prewarm_i>=DISTRICTS_NEEDED and roads.size()>=ROAD_COUNT'''
assert t.count(old_tick) == 1, t.count(old_tick)
t = t.replace(old_tick, new_tick, 1)

# --- 3) warm one zombie model per frame during the same screen, so the first spawn never stalls
old_pre = '''	var prewarm_part: float = float(mini(district_prewarm_i, DISTRICTS_NEEDED)) / float(DISTRICTS_NEEDED)'''
new_pre = '''	if loading_target=="run":
		_warm_up_tick()
	var prewarm_part: float = float(mini(district_prewarm_i, DISTRICTS_NEEDED)) / float(DISTRICTS_NEEDED)'''
assert t.count(old_pre) == 1
t = t.replace(old_pre, new_pre, 1)

# the progress bar should reflect the street too
old_prog = '''	loading_progress = minf(0.98, maxf(loading_time/maxf(loading_duration,0.01), prewarm_part if loading_target=="run" else 0.0))'''
new_prog = '''	var road_part: float = float(roads.size()) / float(ROAD_COUNT) if loading_target=="run" else 0.0
	loading_progress = minf(0.98, maxf(maxf(loading_time/maxf(loading_duration,0.01), prewarm_part if loading_target=="run" else 0.0), road_part))'''
assert t.count(old_prog) == 1
t = t.replace(old_prog, new_prog, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("road build and zombie warm-up spread across the run loading screen")
