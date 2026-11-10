import io

P = r"C:\Users\user\Documents\kimi\tasks\2026-11-06\12-50-12-52283f1e\df-backup\scripts\main_3d.gd"
t = io.open(P, encoding="utf-8").read()

# add a real, rendered gate to the loading warm-up (this viewport actually draws every item, which
# is what uploads geometry and bakes the text)
if 'warmup_queue.append("gate")' not in t:
    old = '\twarmup_queue.append("effects")'
    assert t.count(old) == 1
    t = t.replace(old, old + '\n\twarmup_queue.append("gate")', 1)

if 'if item=="gate":' not in t:
    old_eff = '''		return
	var n: Node3D=null'''
    new_eff = '''		return
	if item=="gate":
		var gids: Array = []
		for id in BuffCatalog.BUFFS.keys():
			gids.append(id)
		var k2 := 0
		while k2 < gids.size():
			var opts: Array = []
			for id2 in gids.slice(k2, mini(k2 + 3, gids.size())):
				opts.append(_gate_option(String(id2), 3))
			var gw: Node3D = GateScript.new()
			gw.position = Vector3(0, 0, -2.0 - 0.5 * float(k2))
			warmup_root.add_child(gw)
			if gw.has_method("setup"):
				gw.setup(opts, language_code)
			k2 += 3
		return
	var n: Node3D=null'''
    assert t.count(old_eff) == 1
    t = t.replace(old_eff, new_eff, 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("gates are now drawn once during the loading warm-up")
