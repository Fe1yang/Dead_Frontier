import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# state: three crates a day, and one only every five runs
if "airdrop_count_today" not in t:
    old = 'var airdrop_day:=""'
    new = ('var airdrop_day:=""\n'
           '## Supply crates: three a day, and only every fifth run.\n'
           'var airdrop_count_today:=0\n'
           'var runs_total:=0\n'
           'var airdrop_at_run:=-5')
    assert t.count(old) == 1
    t = t.replace(old, new, 1)

# availability
old_av = '''func airdrop_available() -> bool:
	return airdrop_day!=today()'''
new_av = '''func airdrop_available() -> bool:
	if airdrop_day!=today():
		airdrop_day=today()
		airdrop_count_today=0
	if airdrop_count_today>=3:
		return false
	return runs_total-airdrop_at_run>=5'''
assert t.count(old_av) == 1, t.count(old_av)
t = t.replace(old_av, new_av, 1)

# consumption
old_open = '''	airdrop_day=today(); airdrop_reward=_roll_airdrop()'''
new_open = '''	airdrop_day=today(); airdrop_reward=_roll_airdrop()
	airdrop_count_today+=1; airdrop_at_run=runs_total'''
assert t.count(old_open) == 1, t.count(old_open)
t = t.replace(old_open, new_open, 1)

# count every run started
old_run = "\truns_this_launch+=1; run_start_best=best_distance; new_record=false; record_banner=0.0"
new_run = "\truns_this_launch+=1; runs_total+=1; run_start_best=best_distance; new_record=false; record_banner=0.0"
assert t.count(old_run) == 1
t = t.replace(old_run, new_run, 1)

# persist
if 'set_value("run","runs_total"' not in t:
    old_save = 'c.set_value("can_ads","day",can_ad_day); c.set_value("can_ads","count",can_ad_count)'
    new_save = (old_save + '\n\tc.set_value("crates","day",airdrop_day); c.set_value("crates","count",airdrop_count_today);'
                '\n\tc.set_value("crates","runs",runs_total); c.set_value("crates","at_run",airdrop_at_run)')
    assert t.count(old_save) == 1
    t = t.replace(old_save, new_save, 1)

if "crates\",\"count\"" not in t.split("func _load")[1][:4000]:
    old_load = '\t\tterms_accepted=bool(c.get_value("legal","terms_v1",false))'
    new_load = (old_load + '\n\t\tairdrop_day=String(c.get_value("crates","day",""))'
                '\n\t\tairdrop_count_today=int(c.get_value("crates","count",0))'
                '\n\t\truns_total=int(c.get_value("crates","runs",0))'
                '\n\t\tairdrop_at_run=int(c.get_value("crates","at_run",-5))')
    assert t.count(old_load) == 1
    t = t.replace(old_load, new_load, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("supply crates: 3 per day, every 5 runs")
