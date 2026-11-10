import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

if 'warmup_queue.append("bike")' not in t:
    old = '\twarmup_queue.append("barrel_roll")'
    assert t.count(old) == 1
    t = t.replace(old, old + '\n\twarmup_queue.append("bike")', 1)

if 'if item=="bike":' not in t:
    old_g = '''	if item=="barrel_roll":'''
    new_g = '''	if item=="bike":
		# the three rideable bikes: their GLBs are what has to be uploaded before a bike crate
		for k3 in range(3):
			var bpath := "res://assets/models/vehicles/bike_paid%s.glb" % ("" if k3 == 0 else str(k3 + 1))
			if not ResourceLoader.exists(bpath):
				continue
			var bk: Node3D = (load(bpath) as PackedScene).instantiate() as Node3D
			if bk == null:
				continue
			bk.position = Vector3(-1.6 + 1.6 * float(k3), 0, -2.0)
			warmup_root.add_child(bk)
		return
	if item=="barrel_roll":'''
    assert t.count(old_g) == 1
    t = t.replace(old_g, new_g, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("bikes added to the warm-up")
