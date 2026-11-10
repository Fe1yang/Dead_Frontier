import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "func _warm_drop_pool" not in t:
    helper = '''## Build the drop props once, during loading, and keep them for reuse: creating the crate model
## mid-run was the last 150 ms stall in the frame trace.
func _warm_drop_pool() -> void:
	for i in range(3):
		var c := WeaponCrateScript.new()
		add_child(c)
		c.setup("SMG", 3)
		c.visible = false
		c.position = Vector3(0, -50, 0)
		crate_pool.append(c)
	for i in range(3):
		var b := BarrelScript.new()
		add_child(b)
		b.visible = false
		b.position = Vector3(0, -50, 0)
		barrel_pool.append(b)


'''
    anchor = "func _finish_loading() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

# run it as the loading screen closes
old = "\tdistricts_ready = true"
if "PREM_WARM_POOL" not in t:
    idx = t.find("func _finish_loading() -> void:")
    body = t[idx:idx + 700]
    if "_warm_drop_pool()" not in body:
        # insert right after the function signature line
        line_end = t.find("\n", idx)
        t = t[:line_end + 1] + "\tif PREMIUM_OR_NOT:\n\t\t_warm_drop_pool()\n" + t[line_end + 1:]

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("drop pool warms during loading")
