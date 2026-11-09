import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "PERF_TRACE" not in t:
    helper = '''## Set PERF_TRACE=1 in the environment to log anything that blocks a frame for over 50 ms.
func _perf_trace(label: String, started_usec: int) -> void:
	if not OS.has_environment("PERF_TRACE"):
		return
	var ms := (Time.get_ticks_usec() - started_usec) / 1000.0
	if ms > 50.0:
		print("PERF_SPIKE ", label, " ", snappedf(ms, 0.1), " ms")


'''
    anchor = "func _build_district(i: int) -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

# time the district build
old = '''	var road:=packed.instantiate() as Node3D'''
new = '''	var _t0 := Time.get_ticks_usec()
	var road:=packed.instantiate() as Node3D
	_perf_trace("district_instantiate", _t0)'''
assert t.count(old) == 1
t = t.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("district build is traced")
