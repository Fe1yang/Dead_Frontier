import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "lamp_style" not in t:
    anchor = "\t# --- things that stand against the buildings"
    assert t.count(anchor) == 1
    lamps = '''	# --- lamps: three block styles, so the lighting differs from street to street -------------
	# Placed near the kerb, in world space, on the pavement (kerb 4.36, buildings ~7.8).
	var lamp_style: int = index % 3
	if lamp_style != 2:
		var lamp_name: String = "lamp_modern" if lamp_style == 0 else "lamp_round"
		for side in [-1.0, 1.0]:
			_prop_node(lamp_name, road, Vector3(side * 5.20, PAVEMENT_Y, base_z + 2.4), 0.0)
			_prop_node(lamp_name, road, Vector3(side * 5.20, PAVEMENT_Y, base_z - 5.4), 0.0)
'''
    t = t.replace(anchor, lamps + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("lamp styles restored at world coordinates on the pavement")
else:
    print("lamps already present")
