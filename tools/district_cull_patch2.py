import io

p = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(p, encoding="utf-8").read()

if "func _cull_districts" not in t:
    helper = '''## Whole-district culling. Per-mesh visibility ranges only save the renderer work; switching a
## district node off skips its ~45 meshes outright.
const DISTRICT_CULL := 120.0


func _cull_districts() -> void:
	for r in roads:
		if not is_instance_valid(r):
			continue
		r.visible = absf(r.position.z) < DISTRICT_CULL


'''
    anchor = "func _build_road() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

old = "\tplayer.set_aim(aim_direction); player.tick(delta); shot_timer-=delta"
assert t.count(old) == 1
t = t.replace(old, "\t_cull_districts()\n" + old, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("district level culling added to the frame tick")
