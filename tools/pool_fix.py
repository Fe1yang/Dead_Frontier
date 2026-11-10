import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

broken = '''		var crate: Node3D
	if crate_pool.is_empty():
		crate = WeaponCrateScript.new(); add_child(crate)
	else:
		crate = crate_pool.pop_back()
		crate.visible = true
	var id: String=choices[used%choices.size()]; used+=1'''
fixed = '''		var crate: Node3D
		if crate_pool.is_empty():
			crate = WeaponCrateScript.new(); add_child(crate)
		else:
			crate = crate_pool.pop_back()
			crate.visible = true
		var id: String=choices[used%choices.size()]; used+=1'''
assert t.count(broken) == 1, t.count(broken)
t = t.replace(broken, fixed, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("indentation repaired")
