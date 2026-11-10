import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- pools
if "var crate_pool" not in t:
    anchor = "var barrels: Array=[]"
    assert t.count(anchor) == 1
    t = t.replace(anchor, anchor + ("\n## Reused drop props: instantiating the 5 MB crate during a run cost ~150 ms a time.\n"
                                    "var crate_pool: Array=[]\nvar barrel_pool: Array=[]"), 1)

# ---------------------------------------------------------------- take from the pool first
old_barrel = "\tvar barrel:=BarrelScript.new(); barrel.position=Vector3(x,0,-45); add_child(barrel); barrels.append(barrel)"
new_barrel = '''	var barrel: Node3D
	if barrel_pool.is_empty():
		barrel = BarrelScript.new(); add_child(barrel)
	else:
		barrel = barrel_pool.pop_back()
	barrel.position = Vector3(x, 0, -45)
	barrel.visible = true
	if barrel.has_method("setup"): barrel.setup()
	barrels.append(barrel)'''
assert t.count(old_barrel) == 1, t.count(old_barrel)
t = t.replace(old_barrel, new_barrel, 1)

old_crate = '''	var crate:=WeaponCrateScript.new(); var id: String=choices[used%choices.size()]; used+=1'''
new_crate = '''	var crate: Node3D
	if crate_pool.is_empty():
		crate = WeaponCrateScript.new(); add_child(crate)
	else:
		crate = crate_pool.pop_back()
		crate.visible = true
	var id: String=choices[used%choices.size()]; used+=1'''
assert t.count(old_crate) == 1, t.count(old_crate)
t = t.replace(old_crate, new_crate, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("drops now come from a pool when one is available")
