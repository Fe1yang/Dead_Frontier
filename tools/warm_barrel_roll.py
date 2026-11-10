import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# ---- item 1: rolling barrel ----
if 'warmup_queue.append("barrel_roll")' not in t:
    old = '\twarmup_queue.append("gate")'
    assert t.count(old) == 1
    t = t.replace(old, old + '\n\twarmup_queue.append("barrel_roll")', 1)

if 'if item=="barrel_roll":' not in t:
    old_g = '''	if item=="gate":'''
    new_g = '''	if item=="barrel_roll":
		var br: Node3D = BarrelRollScript.new()
		br.setup("SHOTGUN", 3)
		br.position = Vector3(1.6, 0, -2.0)
		warmup_root.add_child(br)
		return
	if item=="gate":'''
    assert t.count(old_g) == 1
    t = t.replace(old_g, new_g, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("rolling barrel added to the warm-up")
