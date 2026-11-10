import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

if "func _warm_gates" not in t:
    helper = '''## Gates are built from scratch every time one appears: meshes, Label3D and the font atlas all
## cost their first-use work on that frame. Build a few during loading, covering every rarity the
## gate can show, then throw them away. The real gates find warm caches.
func _warm_gates() -> void:
	var sets := [
		["speed", "damage"],
		["armor", "heal", "firerate"],
		["coins", "magnet"],
	]
	for s in range(sets.size()):
		var opts: Array = []
		for i in range(sets[s].size()):
			opts.append({"id": String(sets[s][i]), "title": "WARM", "detail": "WARM", "rarity": mini(3, s + i)})
		var g: Node3D = GateScript.new()
		g.position = Vector3(0, -60, 0)
		add_child(g)
		if g.has_method("setup"):
			g.setup(opts, language_code)
		g.visible = false
		g.queue_free()


'''
    anchor = "func _finish_loading() -> void:"
    assert t.count(anchor) == 1
    t = t.replace(anchor, helper + anchor, 1)

old = "\t_warm_drop_pool()\n\t_warm_chaser()"
new = "\t_warm_drop_pool()\n\t_warm_chaser()\n\t_warm_gates()"
if t.count(old) == 1:
    t = t.replace(old, new, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("gates are warmed during loading")
