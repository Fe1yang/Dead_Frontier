import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# _ready built all 24 districts synchronously: that is the white-ish freeze on first launch
old_ready = "\t_setup_world(); _build_road()"
new_ready = "\t_setup_world()  # the street is built by the run's loading screen, one district per frame"
assert t.count(old_ready) == 1, t.count(old_ready)
t = t.replace(old_ready, new_ready, 1)

# safety net: if anything reaches the run without a full street, finish it there
old_finish = '''	var target:=loading_target
	loading_progress=1.0'''
new_finish = '''	var target:=loading_target
	if target=="run" and roads.size()<ROAD_COUNT:
		_build_road()
	loading_progress=1.0'''
assert t.count(old_finish) == 1
t = t.replace(old_finish, new_finish, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("_ready no longer builds the street")
