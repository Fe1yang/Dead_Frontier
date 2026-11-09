import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

old = '''	var opening:="clear"
	if runs_this_launch>1:
		var hour_roll:=rng.randf()
		if hour_roll<0.10: opening="dusk"
		elif hour_roll<0.15: opening="dawn"'''
new = '''	var opening:="clear"
	# A brand new player (no best distance yet) always gets a daylight tutorial run.
	var rookie: bool = best_distance <= 0.0 and runs_this_launch <= 2
	if runs_this_launch>1 and not rookie:
		var hour_roll:=rng.randf()
		if hour_roll<0.10: opening="dusk"
		elif hour_roll<0.15: opening="dawn"'''

assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

old2 = '\t\tset_weather("clear" if runs_this_launch==1 else _roll_weather())'
new2 = '\t\tset_weather("clear" if (runs_this_launch==1 or rookie) else _roll_weather())'
assert t.count(old2) == 1
t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("rookie runs start in daylight")
