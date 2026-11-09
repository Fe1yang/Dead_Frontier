import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

# 1) obstacle pop-up labels were hardcoded English ("CORPSES" leaked into a zh run)
old = '\t\t\t\tvar label: String="POLICE" if obstacle.kind=="police" else ("WRECK" if obstacle.kind=="car" else ("CORPSES" if obstacle.kind=="corpse_pile" else "BARRIER"))'
new = '\t\t\t\tvar label: String=_obstacle_label(String(obstacle.kind))'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)

# 2) helper with zh/en wording (other languages fall back to English)
if "func _obstacle_label" not in t:
    anchor = "func _avoid_obstacles(z: Node3D,delta: float) -> void:"
    assert t.count(anchor) == 1
    helper = '''## Localised label for the obstacle hit pop-up ("CORPSES" used to leak into Chinese runs).
func _obstacle_label(kind: String) -> String:
	var zh := String(language_code).begins_with("zh")
	match kind:
		"police":
			return "警车" if zh else "POLICE"
		"car":
			return "废车" if zh else "WRECK"
		"corpse_pile":
			return "尸堆" if zh else "CORPSES"
		_:
			return "路障" if zh else "BARRIER"


'''
    t = t.replace(anchor, helper + anchor, 1)

# 3) the fuel-can pop-ups were English too
t = t.replace('"FUEL: FULL"', '"油箱加满" if String(language_code).begins_with("zh") else "FUEL: FULL"')
t = t.replace('"FLAME FUEL +100"', '"燃料 +100" if String(language_code).begins_with("zh") else "FLAME FUEL +100"')

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("obstacle and fuel labels localised")
